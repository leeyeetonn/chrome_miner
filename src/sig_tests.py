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


def pairwise(data, d_var, i_var, categories):
    """
    Perform pairwise comparisons

    Args:
        data: data frame
        d_var: dependent variable
        i_var: independent variable
        categories: independent variable categories

    Returns:
        List of tuples of category, category, U value, p value
    """
    results = []
    for i in range(len(categories) - 1):
        for j in range(i+1, len(categories)):
            u_val, p_val = stats.mannwhitneyu(
                    data[data[i_var] == categories[i]][d_var],
                    data[data[i_var] == categories[j]][d_var])
            results.append((categories[i], categories[j], u_val, p_val))
    return results


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
    print("issue type -> number of revisions")
    f_value, p_value = anova(
            data, 'num_revisions', 'final_category', ISSUE_TYPES)
    results = pairwise(
            data, 'num_revisions', 'final_category', ISSUE_TYPES)

    print("\tANOVA:")
    print("\t\tF={}, p={}".format(f_value, p_value))
    print("\tPairwise Comparisons:")
    for r in results:
        print("\t\t{} {} U={}, p={}".format(r[0], r[1], r[2], r[3]))


if __name__ == "__main__":
    """
    Main method
    """
    main(sys.argv)

