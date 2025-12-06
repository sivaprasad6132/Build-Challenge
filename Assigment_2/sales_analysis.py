from __future__ import annotations

import csv
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Iterable, List, Tuple, Callable
from collections import defaultdict
from functools import reduce

@dataclass(frozen=True)
class SaleRecord:
    """
    Immutable data model representing a single sales transaction.
    Each instance corresponds to one row in the sales CSV file.
    """
    product_id: int
    sale_date: datetime
    sales_rep: str
    region: str
    sales_amount: float
    quantity_sold: int
    product_category: str
    unit_cost: float
    unit_price: float
    customer_type: str
    discount: float
    payment_method: str
    sales_channel: str
    region_and_sales_rep: str

    @property
    def profit(self) -> float:
        """
        Compute profit for this record based on unit price, unit cost,
        and quantity sold.
        """
        return (self.unit_price - self.unit_cost) * self.quantity_sold

    @staticmethod
    def from_row(row: Dict[str, str]) -> "SaleRecord":
        """
        Factory method to construct a SaleRecord from a CSV row.

        Args:
            row: A dict mapping CSV column names to string values.

        Returns:
            SaleRecord: Parsed and type-converted record instance.
        """
        # Small parsing helpers to keep construction concise
        parse_int = lambda s: int(s)             # noqa: E731
        parse_float = lambda s: float(s)         # noqa: E731
        parse_date = lambda s: datetime.strptime(s, "%Y-%m-%d")  # noqa: E731

        return SaleRecord(
            product_id=parse_int(row["Product_ID"]),
            sale_date=parse_date(row["Sale_Date"]),
            sales_rep=row["Sales_Rep"].strip(),
            region=row["Region"].strip(),
            sales_amount=parse_float(row["Sales_Amount"]),
            quantity_sold=parse_int(row["Quantity_Sold"]),
            product_category=row["Product_Category"].strip(),
            unit_cost=parse_float(row["Unit_Cost"]),
            unit_price=parse_float(row["Unit_Price"]),
            customer_type=row["Customer_Type"].strip(),
            discount=parse_float(row["Discount"]),
            payment_method=row["Payment_Method"].strip(),
            sales_channel=row["Sales_Channel"].strip(),
            region_and_sales_rep=row["Region_and_Sales_Rep"].strip(),
        )


# -------------------------
# CSV loading (stream-based)
# -------------------------

def load_sales(path: str) -> List[SaleRecord]:
    """
    Load sales data from a CSV file and parse into SaleRecord objects.

    Args:
        path: Path to the CSV file.

    Returns:
        List[SaleRecord]: All records in memory.
    """
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        # Use map + factory method to transform each row into a SaleRecord
        return list(map(SaleRecord.from_row, reader))  # ✅ map used


# -------------------------
# Functional helpers
# -------------------------

def group_by(
    records: Iterable[SaleRecord],
    key_fn: Callable[[SaleRecord], str],
) -> Dict[str, List[SaleRecord]]:
    """
    Group records by a derived key.

    Args:
        records: Iterable of SaleRecord items.
        key_fn: Function that extracts the grouping key from a record.

    Returns:
        Dict[str, List[SaleRecord]]: Mapping of key -> list of records.
    """
    groups: Dict[str, List[SaleRecord]] = defaultdict(list)
    for rec in records:
        groups[key_fn(rec)].append(rec)
    return groups


# -------------------------
# Analytical queries
# -------------------------

def total_sales_and_quantity(records: Iterable[SaleRecord]) -> Tuple[float, int]:
    """
    Compute the total sales amount and total quantity sold.

    Uses map + reduce to demonstrate functional style instead of sum().

    Args:
        records: Iterable of SaleRecord items.

    Returns:
        (total_sales, total_qty)
    """
    total_sales = reduce(
        lambda acc, x: acc + x,
        map(lambda r: r.sales_amount, records),
        0.0,
    )

    total_qty = reduce(
        lambda acc, x: acc + x,
        map(lambda r: r.quantity_sold, records),
        0,
    )

    return total_sales, total_qty


def sales_by_region(records: Iterable[SaleRecord]) -> Dict[str, float]:
    """
    Aggregate total sales amount per region.

    Args:
        records: Iterable of SaleRecord items.

    Returns:
        Dict[region, total_sales]
    """
    # First group by region
    grouped = group_by(records, lambda r: r.region)

    # Then sum sales_amount within each group using map + reduce
    return {
        region: reduce(
            lambda acc, x: acc + x,
            map(lambda r: r.sales_amount, group),
            0.0,
        )
        for region, group in grouped.items()
    }


def profit_by_product_category(records: Iterable[SaleRecord]) -> Dict[str, float]:
    """
    Calculate total profit per product category.

    Args:
        records: Iterable of SaleRecord items.

    Returns:
        Dict[product_category, total_profit]
    """
    grouped = group_by(records, lambda r: r.product_category)

    return {
        category: reduce(
            lambda acc, x: acc + x,
            map(lambda r: r.profit, group),
            0.0,
        )
        for category, group in grouped.items()
    }


def avg_discount_by_customer_type(records: Iterable[SaleRecord]) -> Dict[str, float]:
    """
    Compute average discount given to each customer type.

    Args:
        records: Iterable of SaleRecord items.

    Returns:
        Dict[customer_type, avg_discount]
    """
    grouped = group_by(records, lambda r: r.customer_type)
    result: Dict[str, float] = {}

    for cust_type, group in grouped.items():
        # Extract all discounts for this customer type
        discounts = list(map(lambda r: r.discount, group))
        # Average = sum(discounts) / count
        avg_disc = reduce(lambda a, b: a + b, discounts, 0.0) / len(discounts)
        result[cust_type] = avg_disc

    return result


def top_sales_reps_by_revenue(
    records: Iterable[SaleRecord],
    n: int = 5,
) -> List[Tuple[str, float]]:
    """
    Find the top N sales representatives ranked by revenue.

    Args:
        records: Iterable of SaleRecord items.
        n: Number of top reps to return.

    Returns:
        List of (sales_rep, total_revenue) sorted descending by revenue.
    """
    revenue_by_rep: Dict[str, float] = defaultdict(float)

    # Accumulate revenue per sales rep
    for r in records:
        revenue_by_rep[r.sales_rep] += r.sales_amount

    # Sort by revenue and return top N
    return sorted(
        revenue_by_rep.items(),
        key=lambda kv: kv[1],
        reverse=True,
    )[:n]


def monthly_sales_trend(records: Iterable[SaleRecord]) -> List[Tuple[str, float]]:
    """
    Compute total sales per month (YYYY-MM format), sorted chronologically.

    Args:
        records: Iterable of SaleRecord items.

    Returns:
        List of (month_key, total_sales) sorted by month_key.
    """
    totals: Dict[str, float] = defaultdict(float)

    for r in records:
        # Normalize date to 'YYYY-MM' string key
        month_key = r.sale_date.strftime("%Y-%m")
        totals[month_key] += r.sales_amount

    # Sort by month key for chronological trend
    return sorted(totals.items(), key=lambda kv: kv[0])


def profit_by_sales_channel(records: Iterable[SaleRecord]) -> Dict[str, float]:
    """
    Compute total profit per sales channel (e.g., Online, Retail, etc.).

    Demonstrates use of map, filter, and reduce.

    Args:
        records: Iterable of SaleRecord items.

    Returns:
        Dict[sales_channel, total_profit]
    """
    result: Dict[str, float] = {}

    # Get unique channels (using map to project out sales_channel)
    channels = set(map(lambda r: r.sales_channel, records))  # ✅ map used

    for channel in channels:
        # Filter records belonging to this channel
        filtered = filter(lambda r, ch=channel: r.sales_channel == ch, records)
        # Extract profit values
        profits = map(lambda r: r.profit, filtered)
        # Sum all profits for the channel via reduce
        result[channel] = reduce(lambda a, b: a + b, profits, 0.0)

    return result
