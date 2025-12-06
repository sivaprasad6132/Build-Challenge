import unittest
import tempfile
import os
from datetime import datetime

from sales_analysis import (
    SaleRecord,
    load_sales,
    total_sales_and_quantity,
    sales_by_region,
    profit_by_product_category,
    avg_discount_by_customer_type,
    top_sales_reps_by_revenue,
    monthly_sales_trend,
    profit_by_sales_channel,
)


class SalesAnalysisTests(unittest.TestCase):
    """
    Unit tests for the analytical functions in sales_analysis.py.

    These tests use a small, controlled set of SaleRecord instances
    so that expected values are easy to verify by hand.
    """

    def setUp(self) -> None:
        """
        Create a small in-memory dataset reused across tests.
        """
        self.records = [
            SaleRecord(
                product_id=1,
                sale_date=datetime(2024, 1, 15),
                sales_rep="Alice",
                region="North",
                sales_amount=100.0,
                quantity_sold=2,
                product_category="Electronics",
                unit_cost=30.0,
                unit_price=50.0,
                customer_type="New",
                discount=0.10,
                payment_method="Card",
                sales_channel="Online",
                region_and_sales_rep="North - Alice",
            ),
            SaleRecord(
                product_id=2,
                sale_date=datetime(2024, 1, 20),
                sales_rep="Bob",
                region="South",
                sales_amount=200.0,
                quantity_sold=4,
                product_category="Electronics",
                unit_cost=20.0,
                unit_price=50.0,
                customer_type="Returning",
                discount=0.05,
                payment_method="Cash",
                sales_channel="Retail",
                region_and_sales_rep="South - Bob",
            ),
            SaleRecord(
                product_id=3,
                sale_date=datetime(2024, 2, 5),
                sales_rep="Alice",
                region="North",
                sales_amount=150.0,
                quantity_sold=3,
                product_category="Furniture",
                unit_cost=40.0,
                unit_price=70.0,
                customer_type="New",
                discount=0.00,
                payment_method="Card",
                sales_channel="Online",
                region_and_sales_rep="North - Alice",
            ),
        ]

    # -------------------------
    # Basic property tests
    # -------------------------

    def test_profit_property(self):
        """
        Verify the profit calculation uses:
            (unit_price - unit_cost) * quantity_sold
        """
        r = self.records[0]
        expected = (r.unit_price - r.unit_cost) * r.quantity_sold
        self.assertAlmostEqual(r.profit, expected)

    # -------------------------
    # Analytical function tests
    # -------------------------

    def test_total_sales_and_quantity(self):
        total_sales, total_qty = total_sales_and_quantity(self.records)
        self.assertAlmostEqual(total_sales, 100.0 + 200.0 + 150.0)
        self.assertEqual(total_qty, 2 + 4 + 3)

    def test_sales_by_region(self):
        result = sales_by_region(self.records)
        # North: 100 + 150, South: 200
        self.assertAlmostEqual(result["North"], 250.0)
        self.assertAlmostEqual(result["South"], 200.0)
        self.assertEqual(len(result), 2)

    def test_profit_by_product_category(self):
        result = profit_by_product_category(self.records)
        # Manually compute expected profits:
        # Record 1: (50 - 30) * 2 = 40
        # Record 2: (50 - 20) * 4 = 120
        # Record 3: (70 - 40) * 3 = 90
        electronics_profit = 40 + 120
        furniture_profit = 90

        self.assertAlmostEqual(result["Electronics"], electronics_profit)
        self.assertAlmostEqual(result["Furniture"], furniture_profit)

    def test_avg_discount_by_customer_type(self):
        result = avg_discount_by_customer_type(self.records)

        # New: discounts 0.10 and 0.00 -> avg 0.05
        # Returning: discount 0.05
        self.assertAlmostEqual(result["New"], 0.05)
        self.assertAlmostEqual(result["Returning"], 0.05)

    def test_top_sales_reps_by_revenue(self):
        top_reps = top_sales_reps_by_revenue(self.records, n=2)

        # Totals:
        # Alice: 100 + 150 = 250
        # Bob:   200
        # Expect Alice first
        self.assertEqual(top_reps[0][0], "Alice")
        self.assertAlmostEqual(top_reps[0][1], 250.0)
        self.assertEqual(len(top_reps), 2)

    def test_monthly_sales_trend(self):
        trend = monthly_sales_trend(self.records)

        # January 2024: 100 + 200 = 300
        # February 2024: 150
        expected = [("2024-01", 300.0), ("2024-02", 150.0)]
        self.assertEqual(trend, expected)

    def test_profit_by_sales_channel(self):
        result = profit_by_sales_channel(self.records)

        # Online: records 1 and 3
        # r1 profit: (50 - 30)*2 = 40
        # r3 profit: (70 - 40)*3 = 90
        # Total Online profit = 130
        # Retail: record 2 -> (50 - 20)*4 = 120
        self.assertAlmostEqual(result["Online"], 130.0)
        self.assertAlmostEqual(result["Retail"], 120.0)
        self.assertEqual(len(result), 2)

    # -------------------------
    # CSV loading test
    # -------------------------

    def test_load_sales_parses_rows_correctly(self):
        """
        Integration-style unit test for load_sales:
        - Writes a small CSV to a temp file
        - Calls load_sales(...)
        - Verifies that fields are parsed into a SaleRecord
        """
        header = (
            "Product_ID,Sale_Date,Sales_Rep,Region,Sales_Amount,Quantity_Sold,"
            "Product_Category,Unit_Cost,Unit_Price,Customer_Type,Discount,"
            "Payment_Method,Sales_Channel,Region_and_Sales_Rep\n"
        )
        row = (
            "10,2024-03-01,Charlie,East,500.0,5,"
            "Office,60.0,100.0,New,0.15,"
            "Card,Online,East - Charlie\n"
        )

        with tempfile.NamedTemporaryFile("w", delete=False, suffix=".csv") as tmp:
            tmp.write(header)
            tmp.write(row)
            tmp_path = tmp.name

        try:
            records = load_sales(tmp_path)
            self.assertEqual(len(records), 1)
            rec = records[0]

            self.assertEqual(rec.product_id, 10)
            self.assertEqual(rec.sales_rep, "Charlie")
            self.assertEqual(rec.region, "East")
            self.assertAlmostEqual(rec.sales_amount, 500.0)
            self.assertEqual(rec.quantity_sold, 5)
            self.assertEqual(rec.product_category, "Office")
            self.assertAlmostEqual(rec.unit_cost, 60.0)
            self.assertAlmostEqual(rec.unit_price, 100.0)
            self.assertEqual(rec.customer_type, "New")
            self.assertAlmostEqual(rec.discount, 0.15)
            self.assertEqual(rec.payment_method, "Card")
            self.assertEqual(rec.sales_channel, "Online")
            self.assertEqual(rec.region_and_sales_rep, "East - Charlie")

        finally:
            # Clean up temporary file
            os.remove(tmp_path)


if __name__ == "__main__":
    unittest.main()
