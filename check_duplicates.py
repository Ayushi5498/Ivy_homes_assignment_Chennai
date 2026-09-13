# check_duplicates.py
#
# HOW TO RUN:
#   python check_duplicates.py
#
# Checks listings_all.json (by "listing_id") and projects_all.json (by "project_id")
# for duplicate IDs, then prints a summary for each file.

import json
from collections import Counter


def check_duplicates(filename: str, id_field: str) -> None:
    """Load a JSON file and report duplicate values for the given ID field."""
    print(f"{'═' * 50}")
    print(f"Checking: {filename}  (id field: '{id_field}')")
    print(f"{'─' * 50}")

    with open(filename, "r", encoding="utf-8") as f:
        records = json.load(f)

    total = len(records)

    # Count occurrences of each ID
    id_counts = Counter(r.get(id_field) for r in records)
    unique_ids = len(id_counts)
    duplicates = {id_val: count for id_val, count in id_counts.items() if count > 1}

    if duplicates:
        print(f"Duplicate {id_field}s found:")
        for id_val, count in sorted(duplicates.items(), key=lambda x: -x[1]):
            print(f"  {id_val}  →  {count} times")
    else:
        print(f"No duplicates found.")

    print(f"\nSummary:")
    print(f"  Total records   : {total}")
    print(f"  Unique IDs      : {unique_ids}")
    print(f"  Duplicate IDs   : {len(duplicates)}")
    print()


check_duplicates("listings_all.json", "listing_id")
check_duplicates("rentals_all.json",  "listing_id")
check_duplicates("projects_all.json", "project_id")
