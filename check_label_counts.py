import csv
from collections import Counter

counts = Counter()
with open('data.csv', encoding='utf-8') as f:
    reader = csv.reader(f)
    next(reader, None)
    for r in reader:
        if len(r) >= 2:
            counts[r[-1].strip()] += 1

print(counts)
print('total', sum(counts.values()))
