import csv

with open("movies_huge.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["id", "title", "year"])
    for i in range(1, 1_000_001):
        writer.writerow([i, f"Movie {i}", 1980 + (i % 45)])

print("done writing movies_huge.csv")
