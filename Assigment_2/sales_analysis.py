from __future__ import annotations

import csv
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Iterable, List, Tuple, Callable
from collections import defaultdict
from functools import reduce


# -------------------------
# Domain model
# -------------------------

@dataclass(frozen=True)
class SaleRecord:
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
        return (self.unit_price - self.unit_cost) * self.quantity_sold

    @staticmethod
    def from_row(row: Dict[str, str]) -> "SaleRecord":
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
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return list(map(SaleRecord.from_row, reader))  # ✅ map used


# -------------------------
# Functional helpers
# -------------------------

def group_by(
    records: Iterable[SaleRecord],
    key_fn: Callable[[SaleRecord], str],
) -> Dict[str, List[SaleRecord]]:
    groups: Dict[str, List[SaleRecord]] = defaultdict(list)
    for rec in records:
        groups[key_fn(rec)].append(rec)
    return groups


# -------------------------
# Analytical queries
# -------------------------

def total_sales_and_quantity(records: Iterable[SaleRecord]) -> Tuple[float, int]:
    """
    Uses map + reduce instead of sum directly.
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
    grouped = group_by(records, lambda r: r.region)

    return {
        region: reduce(
            lambda acc, x: acc + x,
            map(lambda r: r.sales_amount, group),
            0.0,
        )
        for region, group in grouped.items()
    }


def profit_by_product_category(records: Iterable[SaleRecord]) -> Dict[str, float]:
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
    grouped = group_by(records, lambda r: r.customer_type)
    result: Dict[str, float] = {}

    for cust_type, group in grouped.items():
        discounts = list(map(lambda r: r.discount, group))
        avg_disc = reduce(lambda a, b: a + b, discounts, 0.0) / len(discounts)
        result[cust_type] = avg_disc

    return result


def top_sales_reps_by_revenue(
    records: Iterable[SaleRecord],
    n: int = 5,
) -> List[Tuple[str, float]]:
    revenue_by_rep: Dict[str, float] = defaultdict(float)

    for r in records:
        revenue_by_rep[r.sales_rep] += r.sales_amount

    return sorted(
        revenue_by_rep.items(),
        key=lambda kv: kv[1],
        reverse=True,
    )[:n]


def monthly_sales_trend(records: Iterable[SaleRecord]) -> List[Tuple[str, float]]:
    totals: Dict[str, float] = defaultdict(float)

    for r in records:
        month_key = r.sale_date.strftime("%Y-%m")
        totals[month_key] += r.sales_amount

    return sorted(totals.items(), key=lambda kv: kv[0])


def profit_by_sales_channel(records: Iterable[SaleRecord]) -> Dict[str, float]:
    result: Dict[str, float] = {}
    channels = set(map(lambda r: r.sales_channel, records))  # ✅ map used

    for channel in channels:
        filtered = filter(lambda r, ch=channel: r.sales_channel == ch, records)
        profits = map(lambda r: r.profit, filtered)

        result[channel] = reduce(lambda a, b: a + b, profits, 0.0)

    return result
