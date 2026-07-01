import csv
import tracemalloc


def read_all_rows(path):
    with open(path) as f:
        reader = csv.DictReader(f)
        rows = []
        for row in reader:
            rows.append(row)
        return rows


tracemalloc.start()

rows = read_all_rows("movies_huge.csv")
print("total rows loaded:", len(rows))

current, peak = tracemalloc.get_traced_memory()
print(f"current memory: {current / 1024 / 1024:.2f} MB")
print(f"peak memory:    {peak / 1024 / 1024:.2f} MB")

tracemalloc.stop()


def read_rows_lazy(path):
    with open(path) as f:
        reader = csv.DictReader(f)
        for row in reader:
            yield row          # <-- pauses here, hands ONE row back, waits


print("\n--- lazy generator version ---")
tracemalloc.start()

count = 0
for row in read_rows_lazy("movies_huge.csv"):
    count += 1

print("total rows processed:", count)

current, peak = tracemalloc.get_traced_memory()
print(f"current memory: {current / 1024 / 1024:.2f} MB")
print(f"peak memory:    {peak / 1024 / 1024:.2f} MB")

tracemalloc.stop()
