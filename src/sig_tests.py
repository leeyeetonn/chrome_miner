#!/bin/env python

import argparse
import pandas
import sys
from scipy import stats

ISSUE_TYPES = ['BUG', 'RFE', 'IMPR', 'REFAC', 'OTHER']


def anova(data, d_var, i_var, categories):
    """
    Perform an ANOVA

    Args:
        data: data frame
        d_var: dependent variable
        i_var: independent variable
        categories: independent variable categories

    Returns:
        tuple of F value, p value
    """
    samples = []
    for c in categories:
        samples.append(data[data[i_var] == c][d_var])
    return stats.f_oneway(*samples)


def main(argv):
    """
    Args:
        argv: preprocessed data file
    """

    if len(argv) < 2:
        print("usage: sig_tests <input file>")
        raise ValueError
    input_file = argv[1]

    data = pandas.read_csv(input_file)

    # ANOVA issue type -> number of revisions
    f_value, p_value = anova(
            data, 'num_revisions', 'final_category', ISSUE_TYPES)
    print("ANOVA for issue type -> number of revisions: F={}, p={}".format(
        f_value, p_value))


if __name__ == "__main__":
    """
    Main method
    """
    main(sys.argv)

