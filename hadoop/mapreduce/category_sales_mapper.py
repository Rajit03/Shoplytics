import sys
import csv

reader = csv.reader(sys.stdin)

# Skip header
next(reader, None)

for row in reader:
    if len(row) >= 2:
        category = row[0].strip()

        try:
            sales = float(row[1])
            print(f"{category}\t{sales}")
        except ValueError:
            continue