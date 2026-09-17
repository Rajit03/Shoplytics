import sys

current_order = None
total_price = 0.0
total_freight = 0.0
total_value = 0.0

for line in sys.stdin:
    line = line.strip()

    if not line:
        continue

    order_id, price, freight, total = line.split("\t")

    price = float(price)
    freight = float(freight)
    total = float(total)

    if current_order == order_id:
        total_price += price
        total_freight += freight
        total_value += total

    else:
        if current_order is not None:
            print(
                f"{current_order}\t"
                f"{total_price:.2f}\t"
                f"{total_freight:.2f}\t"
                f"{total_value:.2f}"
            )

        current_order = order_id
        total_price = price
        total_freight = freight
        total_value = total

if current_order is not None:
    print(
        f"{current_order}\t"
        f"{total_price:.2f}\t"
        f"{total_freight:.2f}\t"
        f"{total_value:.2f}"
    )