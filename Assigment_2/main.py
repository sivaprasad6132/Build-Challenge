from __future__ import annotations
from pathlib import Path
from typing import Dict


from sales_analysis import (
    load_sales,
    total_sales_and_quantity,
    sales_by_region,
    profit_by_product_category,
    avg_discount_by_customer_type,
    top_sales_reps_by_revenue,
    monthly_sales_trend,
    profit_by_sales_channel,
)


# Resolve the base directory dynamically based on the location
# of this script, making the script portable across environments
BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "data" / "sales_data.csv"


def print_mapping(title, mapping, sort_desc=True):
    """
    Pretty-prints a dictionary with aligned columns.
    Args:
        title (str): Title displayed before the output.
        mapping (dict): Key-value pairs to print.
        sort_desc (bool): Whether to sort values in descending order.
    """
    print(f"\n{title}")
    print("-" * len(title))

    # Sort dictionary items by value
    items = sorted(mapping.items(), key=lambda kv: kv[1], reverse=sort_desc)

    # Print key-value pairs in aligned format
    for key, value in items:
        print(f"{key:<20} {value:>15,.2f}")


def main():
    """
    Main entry point for executing all sales analytics and
    printing results to the console.
    """
    # Load sales records from CSV file into memory
    records = load_sales(DATA_PATH)
    print(f"Loaded {len(records)} sales records from {DATA_PATH}\n")

    # Compute total revenue and total quantity sold
    total_sales, total_qty = total_sales_and_quantity(records)
    print(f"Total Sales Amount : {total_sales:,.2f}")
    print(f"Total Quantity Sold: {total_qty:,d}")

    # Sales breakdown by geographic region
    print_mapping("Sales by Region", sales_by_region(records))

    # Profit analysis by product category
    print_mapping(
        "Profit by Product Category",
        profit_by_product_category(records)
    )

    # Average discount grouped by customer type
    avg_disc = avg_discount_by_customer_type(records)
    print("\nAverage Discount by Customer Type")
    print("---------------------------------")
    for cust_type, disc in sorted(avg_disc.items()):
        print(f"{cust_type:<10} {disc:>10.2%}")

    # Top-performing sales representatives ranked by revenue
    print("\nTop 5 Sales Reps by Revenue")
    print("---------------------------")
    for rep, revenue in top_sales_reps_by_revenue(records):
        print(f"{rep:<15} {revenue:>15,.2f}")

    # Month-over-month sales trend
    print("\nMonthly Sales Trend")
    print("-------------------")
    for month, amount in monthly_sales_trend(records):
        print(f"{month}: {amount:>15,.2f}")

    # Profit analysis by sales channel (e.g., Online, Retail, Partner)
    print_mapping(
        "Profit by Sales Channel",
        profit_by_sales_channel(records)
    )




if __name__ == "__main__":
    main()
