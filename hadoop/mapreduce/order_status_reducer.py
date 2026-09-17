import sys

current_status = None
current_count = 0

for line in sys.stdin:
    line = line.strip()

    if not line:
        continue

    status, count = line.split("\t", 1)
    count = int(count)

    if current_status == status:
        current_count += count
    else:
        if current_status is not None:
            print(f"{current_status}\t{current_count}")

        current_status = status
        current_count = count

if current_status is not None:
    print(f"{current_status}\t{current_count}")