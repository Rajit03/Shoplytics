import sys

current_category = None
current_sales = 0.0

for line in sys.stdin:
    line = line.strip()

    if not line:
        continue

    category, sales = line.split("\t", 1)
    sales = float(sales)

    if current_category == category:
        current_sales += sales
    else:
        if current_category is not None:
            print(f"{current_category}\t{current_sales:.2f}")

        current_category = category
        current_sales = sales

if current_category is not None:
    print(f"{current_category}\t{current_sales:.2f}")