import csv
import math
import random
from _csv import reader
from collections import defaultdict
from typing import Dict, Any, Tuple, List

CLIENT_ID, PATH, SENTENCE, UP_VOTES, DOWN_VOTES, AGE, GENDER, ACCENT = range(8)


def read_cv_tsv(cv_tsv: str) -> List[Tuple[str, ...]]:
    with open(cv_tsv) as tsv_file:
        return list(reader(tsv_file, delimiter="\t"))


def group_by(rows: List[Tuple[str, ...]], field=CLIENT_ID) -> Dict[str, Any]:
    """Counts the client ids."""
    grouped = defaultdict(list)
    for row in rows:
        grouped[row[field]].append(row)
    return grouped


def split(rows: List[Tuple[str, ...]],
          dev_pct, test_pct) -> Tuple[List[Tuple[str, ...]], ...]:
    """Splits the rows randomly according to the percentages."""
    num_examples = len(rows)
    index = set(range(num_examples))
    num_dev = math.ceil(dev_pct * num_examples)
    num_test = math.ceil(test_pct * num_examples)
    num_train = num_examples - num_dev - num_test
    assert num_dev > 0 and num_test > 0 and num_train > 0
    dev = random.sample(index, num_dev)
    index = index - set(dev)
    test = random.sample(index, num_test)
    train = index - set(test)

    dev = [rows[i] for i in dev]
    test = [rows[i] for i in test]
    train = [rows[i] for i in train]

    return train, dev, test


def speaker_split(cv_tsv: str,
                  out_train: str,
                  out_dev: str,
                  out_test: str,
                  dev_pct: float,
                  test_pct: float,
                  min_examples: int):
    """Splits the common voice data into train, dev, and test.

    This function ensures that speakers are present across train,
    dev, and test."""
    rows = read_cv_tsv(cv_tsv)
    grouped_by_client = group_by(rows, CLIENT_ID)
    count_sorted = sorted(list(grouped_by_client.items()),
                          key=lambda t: -len(t[1]))
    with open(out_train, "w") as train_f, \
            open(out_dev, "w") as dev_f, \
            open(out_test, "w") as test_f:

        train_writer = csv.writer(train_f, delimiter="\t")
        dev_writer = csv.writer(dev_f, delimiter="\t")
        test_writer = csv.writer(test_f, delimiter="\t")

        for _, rows in count_sorted:
            if len(rows) < min_examples:
                break
            train, dev, test = split(rows, dev_pct, test_pct)
            train_writer.writerows(train)
            dev_writer.writerows(dev)
            test_writer.writerows(test)


def main(cv_tsv, out_train, out_dev, out_test,
         dev_pct, test_pct, min_examples):
    speaker_split(cv_tsv, out_train, out_dev, out_test,
                  float(dev_pct), float(test_pct), int(min_examples))


if __name__ == '__main__':
    import plac

    plac.call(main)
