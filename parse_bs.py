#! /usr/bin/env python3

import csv
from datetime import datetime
import json
import sys
import logging
import os


logging.basicConfig(filename="parse_bs.log", level=logging.DEBUG,
                    format="[ %(asctime)s %(lineno)s:%(filename)s ] - %(message)s", datefmt="%Y-%m-%d")
logger = logging.getLogger(__name__)


CUSTOM_FILENAME = ""
CATEGORY_MAPPING = "categories.json"
STMTS_DIR = "statements"
OUT_FILENAME = f"statement-{datetime.today().strftime('%Y-%m-%d')}"
OUTPUT_DIR = "parsed_data"


if len(sys.argv) == 2:
    CUSTOM_FILENAME = sys.argv[1]


def categorize(description: str) -> str:
    """Check against json mapping file and return category"""
    with open(CATEGORY_MAPPING, "r") as file:
        data = json.loads(file.read())
        for category, keywords in data.items():
            for keyword in keywords:
                if keyword in description.lower():
                    logger.debug(f"Matched description: {description} with category: {category}")
                    return category

    logger.debug(f'Adding {description} as "Extra Expense"')
    return "Extra Expenses"


def _format_date(date_str: str) -> str:
    # format date in format 'YYYYMMDD' to 'YYYY-MM-DD'
    new_date_str = datetime.strftime(datetime.strptime(date_str, "%Y%m%d"), "%Y-%m-%d")
    return new_date_str


def _add_to_sorted(new_data: list, formatted_line: dict) -> list:
    """Adds `formatted_line` item and sorts it in `new_list`"""
    sorted_data = []
    if len(new_data) == 0:
        new_data.append(formatted_line)

    for i in range(len(new_data)):
        # compares the date between each entry already in list and new entry, date in index 2 of each entry
        if new_data[i][2] >= formatted_line[2]:
            sorted_data = new_data[:i] + [formatted_line] + new_data[i:]
            return sorted_data


def format_csv_line(line: list) -> list:
    """Formats the csv list into format for excel spreadsheet

    Takes a list object retrieved from iterating through a csv.reader() obj
    and modifies (item #,card #,transaction date,posting date,transaction amount,description)
    to (description, date[yyyy-mm-dd], category, amount)
    """

    # skip if amount is negative, this means it's a payment or refund to the card
    if float(line[4]) < 0:
        return None

    formatted_line = [line[5], _format_date(line[2]), categorize(line[5]), -(float(line[4]))]

    return formatted_line


def main():
    new_data = []

    stmt_filenames = os.listdir(os.path.join(os.curdir, STMTS_DIR))

    # read through each statement file contained in STMTS_FILENAME
    for f in stmt_filenames:
        # remove any trailing space for each filename read from list file
        logger.info(f"Reading file {f}")
        with open(os.path.join(STMTS_DIR, f.rstrip()), "r") as stmt_file:
            # for each statement file, read contents using csv reader and format each line to the
            reader = csv.reader(stmt_file)

            for line in reader:
                # checking if the csv list contains more than 6 items
                # also discarding line if it's header
                if len(line) >= 6 and "Transaction Date" not in line:
                    # format line
                    formatted_line = format_csv_line(line)
                    
                    if formatted_line:
                        new_data = _add_to_sorted(new_data, formatted_line)

    os.mkdir(OUTPUT_DIR)
    output_filename = f"{OUTPUT_DIR}/{CUSTOM_FILENAME if CUSTOM_FILENAME else OUT_FILENAME}.csv"
    with open(output_filename, "w+") as file:
        logger.info(f"Writing parsed csv data to {output_filename}")
        writer = csv.writer(file)
        writer.writerows(new_data)


if __name__ == "__main__":
    main()
