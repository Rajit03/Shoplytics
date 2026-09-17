import sys
import csv

reader = csv.reader(sys.stdin)

# Skip header
next(reader, None)

for row in reader:
    if len(row) > 2:
        order_status = row[2].strip()

        if order_status:
            print(f"{order_status}\t1")