#!/usr/bin/env python3

import argparse
import csv
import io
import prettytable
import locale
from collections import defaultdict
from typing import Mapping

"""Calculate totals and sub-totals from transactions provided in a CSV file"""


def categorize_transactions(csv_file, category_column, subcategory_column,
                            value_column, delimiter=","
                            ) -> Mapping[str, Mapping[str, float]]:
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
            value = locale.atof(row[value_column])
            sums[category][subcategory] += value
            sums[category]["subtotal"] += value

    return sums


def write_csv(sums: Mapping[str, Mapping[str, float]], f,
              subcategory_column, delimiter=","):
    fieldnames = [subcategory_column] + list(sums.keys())
    writer = csv.DictWriter(f, fieldnames, delimiter=delimiter)
    writer.writeheader()

    for category, subcategories in sums.items():
        for subcategory, sum in subcategories.items():
            if subcategory == "subtotal":
                continue
            row = defaultdict(str)
            row[subcategory_column] = subcategory
            row[category] = locale.format_string("%.2f", sum)
            writer.writerow(row)

    row = defaultdict(str)
    row[subcategory_column] = "Subtotal"
    for category, subcategories in sums.items():
        row[category] = locale.format_string("%.2f", subcategories["subtotal"])
    writer.writerow(row)


def main():
    locale.setlocale(locale.LC_ALL, "")
    if locale.localeconv()["decimal_point"] == ",":
        # CSV delimiter usually is replaced by ; in this case
        default_delimiter = ";"
    else:
        default_delimiter = ","

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("csv_file")
    parser.add_argument("category_column")
    parser.add_argument("subcategory_column")
    parser.add_argument("amount_column")
    parser.add_argument("--delimiter",
                        help="CSV delimiter to use (default: based on locale)",
                        default=default_delimiter)
    parser.add_argument("--output-csv-file")

    args = parser.parse_args()
    sums = categorize_transactions(args.csv_file, args.category_column,
                                   args.subcategory_column, args.amount_column,
                                   args.delimiter)

    if args.output_csv_file:
        def open_output():
            return open(args.output_csv_file, "w+")
        print_table = False
    else:
        def open_output():
            return io.StringIO()
        print_table = True

    with open_output() as f:
        write_csv(sums, f, args.subcategory_column, args.delimiter)

        if print_table:
            f.seek(0)
            print(prettytable.from_csv(f, delimiter=args.delimiter))


if __name__ == "__main__":
    main()
