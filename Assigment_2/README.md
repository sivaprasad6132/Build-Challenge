# Sales Data Analysis Project(Python)


## Dataset Description

This project uses a **Product Sales by Region** dataset containing approximately **1,000 records**.  

### Included Fields
- **Region**
- **Product ID & Product Category**
- **Quantity Sold**
- **Unit Price & Unit Cost**
- **Total Sales Amount**
- **Discounts and Promotions**
- **Customer Type**
- **Sales Channel**
- **Payment Method**
- **Sales Representative**
- **Sale Date**

## Key Analytics Implemented

- **Total Sales Aggregation**  
  Calculates overall revenue and total quantity sold.

- **Regional Performance Analysis**  
  Groups and summarizes sales data by region.

- **High-Value Sales Analysis**  
  Filters and aggregates transactions exceeding a specific value threshold.

- **Profit by Product Category**

- **Top-Performing Sales Representatives**

- **Monthly Sales Trends**

- **Average Discount by Customer Type**

- **Profit by Sales Channel**
---

## Project Structure

```bash
Assigment_2/
├── main.py                 
├── sales_analysis.py       
├── requirements.txt        
├── README.md               
└── data/
    └── sales_data.csv     

```

## 1. Getting Started

### Create and activate a virtual environment

```bash
python3 -m venv venv
source venv/bin/activate       # macOS / Linux
```
### Install dependencies

```bash
pip install -r requirements.txt
```
---

### Run Assignment 2

```bash
cd assignment_2
python main.py
```

#### Sample Console Output

The following console output demonstrates the execution of the sales data analysis pipeline. The application loads the sales dataset, performs multiple aggregation and analytical operations, and prints the computed business insights in a structured and readable format. The output reflects results from grouping, filtering, and reduction operations applied to the dataset.


```text

Total Sales Amount : 5,019,265.23
Total Quantity Sold: 25,355

Sales by Region
---------------
North                   1,369,612.51
East                    1,259,792.93
West                    1,235,608.93
South                   1,154,250.86

Profit by Product Category
--------------------------
Furniture               1,779,461.16
Clothing                1,712,957.80
Electronics             1,574,320.06
Food                    1,421,108.05

Average Discount by Customer Type
---------------------------------
New            15.17%
Returning      15.31%

Top 5 Sales Reps by Revenue
---------------------------
David              1,141,737.36
Bob                1,080,990.63
Eve                  970,183.99
Alice                965,541.77
Charlie              860,811.48

Monthly Sales Trend
-------------------
2023-01:      476,092.36
2023-02:      368,919.36
2023-03:      402,638.77
2023-04:      438,992.61
2023-05:      389,078.76
2023-06:      418,458.34
2023-07:      374,242.88
2023-08:      443,171.28
2023-09:      367,837.60
2023-10:      460,378.78
2023-11:      467,482.90
2023-12:      392,643.58
2024-01:       19,328.01

Profit by Sales Channel
-----------------------
Online                  3,279,015.08
Retail                  3,208,831.99
```


### Run tests

```bash
python -m unittest test_sales_analysis.py
```
## Test Coverage

The following functions and analytical scenarios are covered by unit tests to ensure correctness and reliability of the sales analytics pipeline:

- **total_sales_and_quantity**  
  Validates correct computation of overall revenue and total quantity sold.

- **sales_by_region**  
  Ensures sales aggregation by geographic region is accurate.

- **profit_by_product_category**  
  Verifies profit calculation and aggregation across product categories.

- **avg_discount_by_customer_type**  
  Confirms accurate average discount computation per customer type.

- **top_sales_reps_by_revenue**  
  Tests top-N ranking logic, including cases where `n` exceeds the number of available sales representatives.

- **monthly_sales_trend**  
  Validates correct grouping and chronological ordering of monthly sales totals.

- **profit_by_sales_channel**  
  Ensures profit aggregation works correctly across different sales channels.
