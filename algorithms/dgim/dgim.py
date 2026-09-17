import pandas as pd


# ============================================================
# DGIM ALGORITHM
# ============================================================

class DGIM:

    def __init__(self, window_size):
        self.window_size = window_size
        self.buckets = []
        self.timestamp = 0

    # --------------------------------------------------------
    # Add a new bit to the stream
    # --------------------------------------------------------

    def add_bit(self, bit):

        self.timestamp += 1

        # Only create a bucket when the bit is 1
        if bit == 1:

            # Bucket format:
            # [bucket_size, timestamp]

            self.buckets.insert(
                0,
                [1, self.timestamp]
            )

            self._merge_buckets()

        # Remove buckets outside the window
        self._remove_expired()

    # --------------------------------------------------------
    # Merge buckets
    # --------------------------------------------------------

    def _merge_buckets(self):

        i = 0

        while i < len(self.buckets) - 2:

            # DGIM rule:
            # At most two buckets of the same size

            if (
                self.buckets[i][0]
                == self.buckets[i + 1][0]
                == self.buckets[i + 2][0]
            ):

                new_size = self.buckets[i + 1][0] * 2

                new_timestamp = self.buckets[i + 1][1]

                # Replace the two older buckets
                self.buckets[i + 1] = [
                    new_size,
                    new_timestamp
                ]

                del self.buckets[i + 2]

            else:

                i += 1

    # --------------------------------------------------------
    # Remove expired buckets
    # --------------------------------------------------------

    def _remove_expired(self):

        cutoff = self.timestamp - self.window_size

        self.buckets = [
            bucket
            for bucket in self.buckets
            if bucket[1] > cutoff
        ]

    # --------------------------------------------------------
    # Estimate number of 1s
    # --------------------------------------------------------

    def estimate(self):

        if not self.buckets:
            return 0

        total = 0

        for i, bucket in enumerate(self.buckets):

            size = bucket[0]

            # Oldest bucket may only be partially
            # inside the sliding window

            if i == len(self.buckets) - 1:

                total += size / 2

            else:

                total += size

        return total


# ============================================================
# SHOPLYTICS DGIM
# ============================================================

print("==========================================")
print("       SHOPLYTICS DGIM ALGORITHM")
print("==========================================")


# ============================================================
# INPUT DATA
# ============================================================

input_file = (
    r"C:\Projects\Shoplytics\data\processed"
    r"\orders_clean.csv"
)

print("\nLoading Olist order data...")

print(input_file)

df = pd.read_csv(input_file)

print("\nTotal orders:", len(df))


# ============================================================
# TIMESTAMP PROCESSING
# ============================================================

df["order_purchase_timestamp"] = pd.to_datetime(
    df["order_purchase_timestamp"]
)

# Sort orders chronologically

df = df.sort_values(
    "order_purchase_timestamp"
).reset_index(drop=True)


# ============================================================
# CREATE BINARY STREAM
# ============================================================

# 1 = Delivered order
#
# 0 = Any other order status
#
# Examples:
#
# delivered   -> 1
# canceled    -> 0
# shipped     -> 0
# unavailable -> 0
# processing  -> 0
# etc.

stream = (
    df["order_status"]
    .str.lower()
    .eq("delivered")
    .astype(int)
    .tolist()
)


# ============================================================
# STREAM INFORMATION
# ============================================================

delivered_events = sum(stream)

other_events = len(stream) - delivered_events


print("\n==========================================")
print("E-COMMERCE EVENT STREAM")
print("==========================================")

print("\nEvent definition:")

print("1 = Delivered order")

print("0 = Other order status")

print("\nTotal stream events :", len(stream))

print("Delivered events    :", delivered_events)

print("Other events        :", other_events)


# ============================================================
# DGIM CONFIGURATION
# ============================================================

window_size = 1000


print("\n==========================================")
print("DGIM CONFIGURATION")
print("==========================================")

print("\nSliding window size:", window_size)


# ============================================================
# CREATE DGIM OBJECT
# ============================================================

dgim = DGIM(window_size)


# ============================================================
# PROCESS STREAM
# ============================================================

print("\nProcessing stream...")

for bit in stream:

    dgim.add_bit(bit)


# ============================================================
# ACTUAL COUNT
# ============================================================

recent_window = stream[-window_size:]

actual_delivered = sum(recent_window)


# ============================================================
# DGIM ESTIMATE
# ============================================================

estimated_delivered = dgim.estimate()


# ============================================================
# ERROR CALCULATION
# ============================================================

absolute_error = abs(
    actual_delivered
    - estimated_delivered
)


if actual_delivered > 0:

    percentage_error = (
        absolute_error
        / actual_delivered
    ) * 100

else:

    percentage_error = 0


# ============================================================
# RESULTS
# ============================================================

print("\n==========================================")
print("DGIM RESULTS")
print("==========================================")

print(
    "\nTotal stream events       :",
    len(stream)
)

print(
    "Window size               :",
    window_size
)

print(
    "Actual delivered orders   :",
    actual_delivered
)

print(
    "DGIM estimated orders     :",
    round(estimated_delivered, 2)
)

print(
    "Absolute error            :",
    round(absolute_error, 2)
)

print(
    "Percentage error          :",
    round(percentage_error, 2),
    "%"
)

print(
    "DGIM buckets maintained   :",
    len(dgim.buckets)
)


# ============================================================
# BUCKET INFORMATION
# ============================================================

print("\n==========================================")
print("DGIM BUCKETS")
print("==========================================")

for i, bucket in enumerate(dgim.buckets):

    size = bucket[0]

    timestamp = bucket[1]

    print(
        f"Bucket {i + 1}: "
        f"Size={size}, "
        f"Timestamp={timestamp}"
    )


# ============================================================
# FINAL MESSAGE
# ============================================================

print("\n==========================================")
print(" DGIM EXECUTION COMPLETED SUCCESSFULLY")
print("==========================================")

# ============================================================
# SAVE DGIM RESULTS
# ============================================================

import os

output_dir = r"C:\Projects\Shoplytics\results\dgim"
output_file = os.path.join(output_dir, "dgim_results.csv")

os.makedirs(output_dir, exist_ok=True)

results = pd.DataFrame([{
    "total_stream_events": len(stream),
    "window_size": window_size,
    "actual_delivered_orders": actual_delivered,
    "dgim_estimated_orders": round(estimated_delivered, 2),
    "absolute_error": round(absolute_error, 2),
    "percentage_error": round(percentage_error, 2),
    "dgim_buckets": len(dgim.buckets)
}])

results.to_csv(
    output_file,
    index=False
)

print("\n==========================================")
print("DGIM RESULTS SAVED")
print("==========================================")

print("\nLocal file:")
print(output_file)