#!/usr/bin/env python3

import argparse
import csv
from collections import defaultdict

"""Calculate totals and sub-totals from transactions provided in a CSV file"""


def categorize_transactions(csv_file, category_column, subcategory_column, value_column,
                            delimiter=","):
    with open(csv_file, "r") as f:
        reader = csv.DictReader(f, delimiter=delimiter)

        sums = defaultdict(lambda: defaultdict(float))
        for row in reader:
            category = row[category_column]
            if len(category) == 0:
                continue
            subcategory = row[subcategory_column]
            if subcategory == "subtotal":
                raise ValueError("'subtotal' not allowed as subcategory name")
            value = float(row[value_column].replace(",", "."))
            sums[category][subcategory] += value
            sums[category]["subtotal"] += value

    return sums


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("csv_file")
    parser.add_argument("category_column")
    parser.add_argument("subcategory_column")
    parser.add_argument("amount_column")
    parser.add_argument("--delimiter", default=",")

    args = parser.parse_args()
    print(args.csv_file)
    sums = categorize_transactions(args.csv_file, args.category_column,
                                   args.subcategory_column, args.amount_column,
                                   args.delimiter)

    for category, subcategories in sums.items():
        print(f"{category}:\n")
        for subcategory, sum in subcategories.items():
            if subcategory == "subtotal":
                continue
            print(f"\t{subcategory}: {sum}")

        print("-" * 80)
        print(f"subtotal: {subcategories['subtotal']}")


if __name__ == "__main__":
    main()
