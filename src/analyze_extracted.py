#!/bin/env python

import pandas as pd
import argparse
import matplotlib.pyplot as plt
import os
from scipy import stats
from datetime import datetime
from issue_report import IssueReport

# list of columns we want box plot
BOX_COLUMNS = ['lines_added', 'lines_removed', 'lines_modified', 'num_revisions',
               'num_msg', 'num_unresolved_comments', 'upload_push_timediff']


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

        # time difference in minutes
        timediff = abs(time_obj_1 - time_obj_2).total_seconds()/60
        # round timediff to int
        time_diff_list.append(round(timediff))
    return time_diff_list


def get_lines_modified(df):
    lines_modified = df['lines_added'] + df['lines_removed']
    return lines_modified


def analyze_each_category(df):
    # BUG category
    type_bug_data = df.loc[df['final_category'] == 'BUG']
    bug_reports = IssueReport('Bug', type_bug_data)

    print('BUG median upload -> push timediff = ', bug_reports.median_upush_timediff())
    print('BUG unit test ratio = ', bug_reports.unittest_ratio())

    # RFE category
    type_feature_data = df.loc[df['final_category'] == 'RFE']
    feature_reports = IssueReport('RFE', type_feature_data)
    print('RFE median upload -> push timediff = ', feature_reports.median_upush_timediff())
    print('RFE unit test ratio = ', feature_reports.unittest_ratio())


def clean_null(res_dir, df):
    cleandf = df[df['final_category'].notnull()]
    cleandf = cleandf[cleandf['assigned_category'].notnull()]
    cleandf_outpath = res_dir + '/' + 'clean_null.csv'
    cleandf.to_csv(cleandf_outpath, na_rep='NULL')
    return cleandf


def main():
    parser = argparse.ArgumentParser(description='Read an extracted csv and analyze it')
    parser.add_argument('infile', type=str, help='input csv containing extracted stats')
    parser.add_argument('res_dir', type=str, help='result directory')
    args = parser.parse_args()

    # read extracted stats
    df = read_input(args.infile)

    # remove issue reports that are not accessible
    df = clean_null(args.res_dir, df)

    # get unique issue reports and calculate inter-rater reliability
    agree_perc = get_rater_relibility(df)
    print('Percentage of agreement: %.4f' % agree_perc)

    df['lines_modified'] = get_lines_modified(df)

    # get time difference upload to push
    tdelta = get_time_delta(df['time_uploaded'], df['time_pushed'])
    df['upload_push_timediff'] = tdelta

    res_file_path = args.res_dir + '/' + 'aggregated_result.csv'
    df.to_csv(res_file_path, na_rep='NA')

    # analyze for each category
    analyze_each_category(df)

    # get box plots
    for col in BOX_COLUMNS:
        if col not in df.columns:
            print('Error: requested column "%s" not in data' % col)
            continue
        make_box_plots(args.res_dir, df[col])


if __name__ == '__main__':
    main()
