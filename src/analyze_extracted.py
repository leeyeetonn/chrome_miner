#!/bin/env python

import pandas as pd
from pandas.plotting import scatter_matrix
import numpy as np
import argparse
import matplotlib.pyplot as plt
import os
from scipy import stats
from datetime import datetime
from issue_report import IssueReport

# list of columns we want box plot
BOX_COLUMNS = ['lines_added', 'lines_removed', 'lines_modified', 'num_revisions',
               'num_msg', 'num_unresolved_comments', 'upload_push_timediff']

XLAB_SIZE = 14
YLAB_SIZE = 14
FIG_SIZE = (16, 9)

def test_fexist(fpath):
    if os.path.exists(fpath):
        return True
    print('Error: Given file %s not found.' % fpath)
    return False


def read_input(inpath):
    assert (test_fexist(inpath))
    # read input file as pandas dataframe
    df = pd.read_csv(inpath)
    assert (df is not None)
    return df


def get_rater_relibility(df):
    cols = df.columns
    if 'bug' not in cols or 'disagreement' not in cols:
        print('Error: missing required data for inter-rater reliability')
        return -1

    df_copy = df.copy()
    unique_reports = df_copy.drop_duplicates('bug')
    # for unique issue reports, get disagreement count
    # number of unique reports
    num_unq = unique_reports.hash.count()
    print('number of unique reports = ', num_unq)
    num_agree = unique_reports['disagreement'].value_counts()[False]
    return num_agree / num_unq


def make_box_plots(res_dir, series):
    name = series.name
    k2, p = stats.normaltest(series)
    print('For %s :' % name)
    print(k2, p)
    fig, ax = plt.subplots()
    ax.set_title(name)
    ax.boxplot(series.values)
    image_name = res_dir + "/" + name + ".png"
    plt.savefig(image_name)
    return


def get_time_delta(series1, series2):
    assert(series1.size == series2.size)
    time_format = "%Y-%m-%d %H:%M:%S"
    time_diff_list = []
    for index, time_value_1 in series1.iteritems():
        if time_value_1 == '-1':
            print('Warning: time %s not available, skipping' % time_value_1)
            time_diff_list.append(-1)
            continue
        time_obj_1 = datetime.strptime(time_value_1, time_format)
        time_value_2 = series2.loc[index]
        time_obj_2 = datetime.strptime(time_value_2, time_format)

        # time difference in days
        timediff = abs(time_obj_1 - time_obj_2).total_seconds()/60/60/24
        # round timediff to int
        time_diff_list.append(round(timediff))
    return time_diff_list


def get_lines_modified(df):
    lines_modified = df['lines_added'] + df['lines_removed']
    return lines_modified


def to_reports(col_name, col_value, df):
    data = df.loc[df[col_name] == col_value]
    reports = IssueReport(col_value, data)
    return reports


def to_category_reports(df):
    # RFE
    feature_reports = to_reports('final_category', 'RFE', df)
    print('RFE median upload -> push timediff = ', feature_reports.median_upush_timediff())
    print('RFE unit test ratio = ', feature_reports.unittest_ratio())

    # BUG category
    bug_reports = to_reports('final_category', 'BUG', df)

    print('BUG median upload -> push timediff = ', bug_reports.median_upush_timediff())
    print('BUG unit test ratio = ', bug_reports.unittest_ratio())

    # REFAC category
    refac_reports = to_reports('final_category', 'REFAC', df)
    print('REFAC median upload -> push timediff = ', refac_reports.median_upush_timediff())
    print('REFAC unit test ratio = ', refac_reports.unittest_ratio())

    # IMPR category
    impr_reports = to_reports('final_category', 'IMPR', df)
    print('IMPR median upload -> push timediff = ', impr_reports.median_upush_timediff())
    print('IMPR unit test ratio = ', impr_reports.unittest_ratio())

    reports = {
        "RFE": feature_reports,
        "BUG": bug_reports,
        "REFAC": refac_reports,
        "IMPR": impr_reports
    }

    return reports


def plot_num_revisions(reports):
    data = [r.num_revisions() for r in reports.values()]

    fig, ax = plt.subplots(figsize=FIG_SIZE)

    bp = ax.boxplot(data)
    ax.set_title('Number of revisions for each category')
    ax.set_xticklabels(reports.keys(), fontsize=XLAB_SIZE)
    ax.set_ylabel("number of revisions", fontsize=YLAB_SIZE)

    plt.show()


def plot_upload_push_timediff(reports):
    data = [r.upush_timediff() for r in reports.values()]

    ymax = max([i.max() for i in data])
    fig, ax = plt.subplots(figsize=FIG_SIZE)

    bp = ax.boxplot(data)
    ax.set_title('Time to stay in code review')
    ax.set_yticks(np.arange(0, ymax, 30))
    ax.set_xticklabels(reports.keys(), fontsize=XLAB_SIZE)
    ax.set_ylabel("time span (days)", fontsize=YLAB_SIZE)

    plt.show()


def plot_unittest_ratio(reports):
    data = [r.unittest_ratio() for r in reports.values()]
    num_tested = [r.num_unittested() for r in reports.values()]

    color = ['C0', 'C1', 'C2', 'C3']
    fig, ax = plt.subplots(figsize=FIG_SIZE)
    ind = np.arange(len(reports))

    bars = plt.bar(ind, data)
    ax.set_title('Percentage of unit tested commits in each category')
    ax.set_xticks(ind)
    ax.set_xticklabels(reports.keys(), fontsize=XLAB_SIZE)
    ax.set_ylabel("ratio", fontsize=YLAB_SIZE)

    for c, b in enumerate(bars):
        height = b.get_height()
        b.set_facecolor(color[c])
        ax.text(b.get_x() + b.get_width()/2, 1.01 * height, '{}'.format(num_tested[c]))

    plt.show()


def plot_lines_modified(reports):
    data = [r.lines_modified() for r in reports.values()]

    fig, ax = plt.subplots(figsize=FIG_SIZE)

    bp = ax.boxplot(data)
    ax.set_title('LOC modified for commits in each category')
    ax.set_xticklabels(reports.keys(), fontsize=XLAB_SIZE)
    ax.set_ylabel("LOC", fontsize=YLAB_SIZE)

    plt.show()


def plot_lines_removed(reports):
    data = [r.lines_removed() for r in reports.values()]

    fig, ax = plt.subplots(figsize=FIG_SIZE)

    bp = ax.boxplot(data)
    ax.set_title('LOC removed for commits in each category')
    ax.set_xticklabels(reports.keys(), fontsize=XLAB_SIZE)
    ax.set_ylabel("LOC", fontsize=YLAB_SIZE)

    plt.show()


def plot_lines_added(reports):
    data = [r.lines_added() for r in reports.values()]

    fig, ax = plt.subplots(figsize=FIG_SIZE)

    bp = ax.boxplot(data)
    ax.set_title('LOC added for commits in each category')
    ax.set_xticklabels(reports.keys(), fontsize=XLAB_SIZE)
    ax.set_ylabel("LOC", fontsize=YLAB_SIZE)

    plt.show()


def clean_null(df):
    cleandf = df[df['final_category'].notnull()]
    cleandf = cleandf[cleandf['assigned_category'].notnull()]
    return cleandf


def pairwise_corr_plot(df):
    attrs = ['lines_modified', 'lines_added', 'lines_removed', 'num_comments', 'num_revisions',
             'upload_push_timediff']

    scatter_matrix(df[attrs], figsize=FIG_SIZE)
    plt.show()


def format_ax_lab(key, unit):
    if unit == '':
        return key
    return "{} ({})".format(key, unit)


def scatter_plot(key1, unit1, key2, unit2, df):
    fig, ax = plt.subplots(figsize=FIG_SIZE)
    ax.scatter(df[key1], df[key2])
    xlab = format_ax_lab(key1, unit1)
    ylab = format_ax_lab(key2, unit2)
    ax.set_xlabel(xlab, fontsize=XLAB_SIZE)
    ax.set_ylabel(ylab, fontsize=YLAB_SIZE)
    plt.show()


def get_unittested_vs_non(df):
    unittested = to_reports('is_unittested', True, df)

    # special handling for non_unittested
    part_df = df[df['is_unittested'] == False]
    # not unittested and also not unittest only
    non_unittested = to_reports('is_unittest_only', False, part_df)

    reports = {
        'unittested': unittested,
        'non_unittested': non_unittested
    }

    return reports


def plot_ifunittested_timediff(reports):
    assert(reports is not None and len(reports) != 0)
    data = [r.upush_timediff() for r in reports.values()]

    fig, ax = plt.subplots(figsize=FIG_SIZE)

    bp = ax.boxplot(data)
    ax.set_title('time span from upload to push for unittested and non-unittested commits')
    ax.set_xticklabels(reports.keys(), fontsize=XLAB_SIZE)
    ax.set_ylabel("days", fontsize=YLAB_SIZE)

    plt.show()


def plot_ifunittested_num_comments(reports):
    assert(reports is not None and len(reports) != 0)
    data = [r.num_comments() for r in reports.values()]

    fig, ax = plt.subplots(figsize=FIG_SIZE)

    bp = ax.boxplot(data)
    ax.set_title('number of comments for unittested and non-unittested commits')
    ax.set_xticklabels(reports.keys(), fontsize=XLAB_SIZE)
    ax.set_ylabel("num of comments", fontsize=YLAB_SIZE)

    plt.show()


def plot_ifunittested_num_revisions(reports):
    assert(reports is not None and len(reports) != 0)
    data = [r.num_revisions() for r in reports.values()]

    fig, ax = plt.subplots(figsize=FIG_SIZE)

    bp = ax.boxplot(data)
    ax.set_title('number of revisions for unittested and non-unittested commits')
    ax.set_xticklabels(reports.keys(), fontsize=XLAB_SIZE)
    ax.set_ylabel("num of revisions", fontsize=YLAB_SIZE)

    plt.show()


def preprocess(res_dir, df):
    # drop "OTHER", these are all just git merges
    df = df[df['final_category'] != 'OTHER']

    # remove issue reports that are not accessible
    df = clean_null(df)

    df['lines_modified'] = get_lines_modified(df)

    # get time difference upload to push
    tdelta = get_time_delta(df['time_uploaded'], df['time_pushed'])
    df['upload_push_timediff'] = tdelta

    # aggregated_result.csv will be the final data for all analysis
    res_file_path = res_dir + '/' + 'aggregated_result.csv'
    df.to_csv(res_file_path, na_rep='NA')

    return df


def get_scatter_plots(df):
    pairwise_corr_plot(df)

    scatter_plot('lines_modified', 'LOC', 'num_comments', '', df)
    scatter_plot('lines_modified', 'LOC', 'num_revisions', '', df)
    scatter_plot('lines_modified', 'LOC', 'upload_push_timediff', 'days', df)
    scatter_plot('lines_added', 'LOC', 'num_comments', '', df)
    scatter_plot('num_revisions', '', 'upload_push_timediff', 'days', df)
    scatter_plot('num_comments', '', 'upload_push_timediff', 'days', df)
    scatter_plot('num_comments', '', 'num_revisions', '', df)
    return


def get_class_plots(df):
    reports = to_category_reports(df)

    # box plot for num_revisions for each category
    plot_num_revisions(reports)
    # box plot for upload -> push timediff
    plot_upload_push_timediff(reports)
    # bar chart for unittest ratio
    plot_unittest_ratio(reports)
    # lines_modified for each category
    plot_lines_modified(reports)
    plot_lines_added(reports)
    plot_lines_removed(reports)
    return


def get_unit_plots(df):
    reports = get_unittested_vs_non(df)
    # upload_push_timediff vs. unittested/non_unittested
    plot_ifunittested_timediff(reports)
    # num_comments vs. unittested/non_unittested
    plot_ifunittested_num_comments(reports)
    # num_revisions vs. unittested/non_unittested
    plot_ifunittested_num_revisions(reports)
    return


def main():
    parser = argparse.ArgumentParser(description='Read an extracted csv and analyze it')
    parser.add_argument('infile', type=str, help='input csv containing extracted stats')
    parser.add_argument('res_dir', type=str, help='result directory')
    args = parser.parse_args()

    # read extracted stats
    df = read_input(args.infile)

    # pre-process data
    df = preprocess(args.res_dir, df)

    # get unique issue reports and calculate inter-rater reliability
    agree_perc = get_rater_relibility(df)
    print('Percentage of agreement: %.4f' % agree_perc)

    # ====== START ANALYSIS ======
    # scatter plot
    get_scatter_plots(df)

    # distribution across manual classification category
    get_class_plots(df)

    # distribution in unit test vs not unit tested
    get_unit_plots(df)

    # get box plots
    for col in BOX_COLUMNS:
        if col not in df.columns:
            print('Error: requested column "%s" not in data' % col)
            continue
        make_box_plots(args.res_dir, df[col])


if __name__ == '__main__':
    main()
