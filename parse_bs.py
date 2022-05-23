#! /usr/bin/env python3

import csv
from datetime import datetime
import json
import sys
import logging
import math

from black import NewLine


logging.basicConfig(filename="parse_bs.log", level=logging.DEBUG,
                    format="[ %(asctime)s %(lineno)s:%(filename)s ] - %(message)s", datefmt="%Y-%m-%d")
logger = logging.getLogger(__name__)


CUSTOM_FILENAME = ""
CATEGORY_MAPPING = "categories.json"
STMTS_FILENAME = "statement_list.txt"
OUT_FILENAME = f"statement-{datetime.today().strftime('%Y-%m-%d')}"


if len(sys.argv) == 2:
    CUSTOM_FILENAME = sys.argv[1]


def categorize(description: str) -> str:
    """Check against json mapping file and return category"""
    with open(CATEGORY_MAPPING, "r") as file:
        data = json.loads(file.read())
        for category, keywords in data.items():
            for keyword in keywords:
                if keyword in description.lower():
                    logger.debug(f"Categorized description: {description} to category: {category}")
                    return category

    logger.debug(f'Adding {description} as "Extra Expense"')
    return "Extra Expenses"


def _get_date(date_str: str) -> str:
    # format date in format 'YYYYMMDD' to 'YYYY-MM-DD'
    new_date_str = datetime.strftime(datetime.strptime(date_str, "%Y%m%d"), "%Y-%m-%d")
    return new_date_str


def _mergesort(csv_list: list) -> list:
    """Uses merge sort to sort a csv list item based on the date element"""
    if len(csv_list) > 1:
        mid_index = math.floor(len(csv_list)/2)
        left_hand_list = csv_list[mid_index:]
        right_hand_list = csv_list[:mid_index]
        left_sorted = _mergesort(left_hand_list)
        right_sorted = _mergesort(right_hand_list)
        return merge()
    else:
        return csv_list


def _get_sorted_csv_list(new_data: list) -> list:
    """Sorts the list of csv items using the date element"""
    pass


def format_csv_line(line: list) -> list:
    """Formats the csv list into format for excel spreadsheet

    Takes a list object retrieved from iterating through a csv.reader() obj
    and modifies (item #,card #,transaction date,posting date,transaction amount,description)
    to (description, date[yyyy-mm-dd], category, amount)
    """
    # skip if amount is negative, this means it's a payment or refund to the card
    if float(line[4]) < 0:
        return None
    new_line = [line[5], _get_date(line[2]), categorize(line[5]), -(float(line[4]))]

    return new_line


def main():
    # TODO: make this dictionary usable
    new_data_sorted = {}
    new_data = []

    with open(STMTS_FILENAME) as stmt_file:
        stmt_filenames: str = stmt_file.readlines()
        for f in stmt_filenames:
            # remove any trailing space for each filename read from list file
            logger.info(f"Reading file {f}")
            with open(f.rstrip(), "r") as stmt_file:
                reader = csv.reader(stmt_file)

                for line in reader:
                    # checking if the csv list contains more than 6 items
                    # also discarding line if it's header
                    if len(line) >= 6 and "Transaction Date" not in line:
                        # create a dictionary to store date as key=value pair and sort dict based on that
                        new_line = format_csv_line(line)

                        if new_line:
                            new_data.append(new_line)
                            # TODO: reintegrate these lines when the mergesort is implemented
                            # new_data["date"] = new_line[1]
                            # new_data["csv_item"] = new_line

    output_file = f"{CUSTOM_FILENAME if CUSTOM_FILENAME else OUT_FILENAME}.csv"
    with open(output_file, "w+") as file:
        logger.info(f"Writing parsed csv data to {output_file}")
        writer = csv.writer(file)
        writer.writerows(new_data)


if __name__ == "__main__":
    main()
