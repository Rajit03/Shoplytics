import sys
import csv

reader = csv.reader(sys.stdin)

# Skip header
next(reader, None)

for row in reader:
    if len(row) >= 8:
        order_id = row[0].strip()

        try:
            price = float(row[5])
            freight = float(row[6])
            total = float(row[7])

            print(f"{order_id}\t{price}\t{freight}\t{total}")

        except ValueError:
            continue