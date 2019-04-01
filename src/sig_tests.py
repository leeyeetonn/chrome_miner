#!/bin/env python

import argparse
import pandas
import sys
from scipy import stats

ISSUE_TYPES = ['BUG', 'RFE', 'IMPR', 'REFAC']


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


def correlate(data, x_var, y_var):
    """
    Correlate two variables

    Args:
        data: data frame
        x_var: first variable
        y_var: second variable

    Returns:
        Tuple of Pearson's correlation coefficient, p_value
    """
    x = data[x_var]
    y = data[y_var]
    return stats.pearsonr(x, y)


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
    print("issue type -> change size")
    f_value, p_value = anova(
            data, 'lines_modified', 'final_category', ISSUE_TYPES)
    results = pairwise(
            data, 'lines_modified', 'final_category', ISSUE_TYPES)
    print("\tANOVA:")
    print("\t\tF={}, p={}".format(f_value, p_value))
    print("\tPairwise Comparisons:")
    for r in results:
        print("\t\t{} {} U={}, p={}".format(r[0], r[1], r[2], r[3]))
    print()

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
    print()

    # ANOVA issue type -> number of comments
    print("issue type -> number of comments")
    f_value, p_value = anova(
            data, 'num_comments', 'final_category', ISSUE_TYPES)
    results = pairwise(
            data, 'num_comments', 'final_category', ISSUE_TYPES)
    print("\tANOVA:")
    print("\t\tF={}, p={}".format(f_value, p_value))
    print("\tPairwise Comparisons:")
    for r in results:
        print("\t\t{} {} U={}, p={}".format(r[0], r[1], r[2], r[3]))
    print()

    # ANOVA issue type -> time in review
    print("issue type -> time in review")
    f_value, p_value = anova(
            data, 'upload_push_timediff', 'final_category', ISSUE_TYPES)
    results = pairwise(
            data, 'upload_push_timediff', 'final_category', ISSUE_TYPES)
    print("\tANOVA:")
    print("\t\tF={}, p={}".format(f_value, p_value))
    print("\tPairwise Comparisons:")
    for r in results:
        print("\t\t{} {} U={}, p={}".format(r[0], r[1], r[2], r[3]))
    print()

    # Correlate lines modified with number of comments
    print("correlate lines modified w/ number of comments")
    r_value, p_value = correlate(data, 'lines_modified', 'num_comments')
    print("\tr={}, p={}".format(r_value, p_value))
    print()

    # Correlate lines added with number of comments
    print("correlate lines added w/ number of comments")
    r_value, p_value = correlate(data, 'lines_added', 'num_comments')
    print("\tr={}, p={}".format(r_value, p_value))
    print()

    # Correlate lines removed with number of comments
    print("correlate lines removed w/ number of comments")
    r_value, p_value = correlate(data, 'lines_removed', 'num_comments')
    print("\tr={}, p={}".format(r_value, p_value))
    print()

    # Correlate lines modified with number of revisions
    print("correlate lines modified w/ number of revisions")
    r_value, p_value = correlate(data, 'lines_modified', 'num_revisions')
    print("\tr={}, p={}".format(r_value, p_value))
    print()

    # Correlate lines added with number of revisions
    print("correlate lines added w/ number of revisions")
    r_value, p_value = correlate(data, 'lines_added', 'num_revisions')
    print("\tr={}, p={}".format(r_value, p_value))
    print()

    # Correlate lines removed with number of revisions
    print("correlate lines removed w/ number of revisions")
    r_value, p_value = correlate(data, 'lines_removed', 'num_revisions')
    print("\tr={}, p={}".format(r_value, p_value))
    print()

    # Correlate lines modified with time to submit
    print("correlate lines modified w/ time to submit")
    r_value, p_value = correlate(data, 'lines_modified', 'upload_push_timediff')
    print("\tr={}, p={}".format(r_value, p_value))
    print()

    # Correlate lines added with time to submit
    print("correlate lines added w/ number of comments")
    r_value, p_value = correlate(data, 'lines_added', 'upload_push_timediff')
    print("\tr={}, p={}".format(r_value, p_value))
    print()

    # Correlate lines removed with time to submit
    print("correlate lines removed w/ number of comments")
    r_value, p_value = correlate(data, 'lines_removed', 'upload_push_timediff')
    print("\tr={}, p={}".format(r_value, p_value))
    print()

    # Correlate number of comments with time to submit
    print("correlate number of comments w/ time to submit")
    r_value, p_value = correlate(data, 'num_comments', 'upload_push_timediff')
    print("\tr={}, p={}".format(r_value, p_value))
    print()

    # Correlate number of revisions with time to submit
    print("correlate number of revisions w/ time to submit")
    r_value, p_value = correlate(data, 'num_revisions', 'upload_push_timediff')
    print("\tr={}, p={}".format(r_value, p_value))
    print()

    # Correlate number of revisions with number of comments
    print("correlate number of comments w/ number of revisions")
    r_value, p_value = correlate(data, 'num_revisions', 'num_comments')
    print("\tr={}, p={}".format(r_value, p_value))
    print()

    # Time to submit based on whether a change is unit tested
    print("time to submit based on whether a change is unit tested")
    ut_data = data[data['is_unittest_only'] == False]
    u_value, p_value = stats.mannwhitneyu(
            ut_data[ut_data['is_unittested'] == True]['upload_push_timediff'],
            ut_data[ut_data['is_unittested'] == False]['upload_push_timediff'])
    print("\tU={}, p={}".format(u_value, p_value))
    print()

    # Number of comments based on whether a change is unit tested
    print("number of comments based on whether a change is unit tested")
    ut_data = data[data['is_unittest_only'] == False]
    u_value, p_value = stats.mannwhitneyu(
            ut_data[ut_data['is_unittested'] == True]['num_comments'],
            ut_data[ut_data['is_unittested'] == False]['num_comments'])
    print("\tU={}, p={}".format(u_value, p_value))
    print()

    # Remove changes that are only unit tests
    ut_data = data[data['is_unittest_only'] == False]

    # Time to submit based on whether a change is unit tested
    print("number of revisions based on whether a change is unit tested")
    u_value, p_value = stats.mannwhitneyu(
            ut_data[ut_data['is_unittested'] == True]['num_revisions'],
            ut_data[ut_data['is_unittested'] == False]['num_revisions'])
    print("\tU={}, p={}".format(u_value, p_value))
    print()

    # Unit tested based on issue type
    print("unit tested based on issue type")
    unittest_cats = []
    unittest_expt = []

    total_unittested = ut_data['is_unittested'].sum()
    ut_ratio = total_unittested / len(ut_data)

    for c in ISSUE_TYPES:
        cat_data = ut_data[ut_data['final_category'] == c]['is_unittested']
        unittest_cats.append(cat_data.sum())
        unittest_expt.append(int(len(cat_data) * ut_ratio)) 

    chi_sqr, p_value = stats.chisquare(unittest_cats, unittest_expt)
    print("\tchisqr={}, p={}".format(chi_sqr, p_value))


if __name__ == "__main__":
    """
    Main method
    """
    main(sys.argv)

