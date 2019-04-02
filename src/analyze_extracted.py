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

TITLE_SIZE = 28
XLAB_SIZE = 28
YLAB_SIZE = 28
FIG_SIZE = (16, 9)
TICK_SIZE = 25
BAR_NUM_SIZE = 22

CAT_MAP = {'Feature': 'RFE', 'Bug': 'BUG'}

COL_MAP = {'lines_added': 'Added LOC',
           'lines_removed': 'Removed LOC',
           'num_revisions': 'Revisions',
           'lines_modified': 'Modified LOC',
           'num_comments': 'Code Review Comments',
           'upload_push_timediff': 'Time in Review'
           }

UTEST_MAP = {'unittested': 'Unit Tested', 'non_unittested': 'Not Unit Tested'}


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
    return num_agree / num_unq, unique_reports


#def make_box_plots(res_dir, series):
#    name = series.name
#    k2, p = stats.normaltest(series)
#    print('For %s :' % name)
#    print(k2, p)
#    fig, ax = plt.subplots()
#    ax.set_title(name, fontsize=TITLE_SIZE)
#    ax.boxplot(series.values)
#    ax.tick_params(labelsize=TICK_SIZE)
#    image_name = res_dir + "/" + name + ".png"
#    plt.savefig(image_name)
#    plt.close()
#    return


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

    # BUG category
    bug_reports = to_reports('final_category', 'BUG', df)

    # REFAC category
    refac_reports = to_reports('final_category', 'REFAC', df)

    # IMPR category
    impr_reports = to_reports('final_category', 'IMPR', df)

    reports = {
        "RFE": feature_reports,
        "BUG": bug_reports,
        "REFAC": refac_reports,
        "IMPR": impr_reports
    }

    return reports


def plot_num_revisions(res_dir, reports):
    data = [r.num_revisions() for r in reports.values()]

    fig, ax = plt.subplots(figsize=FIG_SIZE)

    bp = ax.boxplot(data)
    #ax.set_title('Number of revisions for each category', fontsize=TITLE_SIZE)
    ax.set_xticklabels(reports.keys(), fontsize=XLAB_SIZE)
    ax.set_ylabel("Revisions", fontsize=YLAB_SIZE)
    ax.tick_params(labelsize=TICK_SIZE)

    image_name = res_dir + '/' + 'revisions_vs_class.png'
    plt.savefig(image_name)
    plt.close()


def plot_upload_push_timediff(res_dir, reports):
    data = [r.upush_timediff() for r in reports.values()]

    ymax = max([i.max() for i in data])
    fig, ax = plt.subplots(figsize=FIG_SIZE)

    bp = ax.boxplot(data)
    #ax.set_title('Time to stay in code review', fontsize=TITLE_SIZE)
    ax.set_yticks(np.arange(0, ymax, 30))
    ax.set_xticklabels(reports.keys(), fontsize=XLAB_SIZE)
    ax.set_ylabel("Time in Review (days)", fontsize=YLAB_SIZE)
    ax.tick_params(labelsize=TICK_SIZE)

    image_name = res_dir + '/' + 'timediff_vs_class.png'
    plt.savefig(image_name)
    plt.close()


def plot_unittest_ratio(res_dir, reports):
    data = [r.unittest_ratio() for r in reports.values()]
    num_tested = [r.num_unittested() for r in reports.values()]

    color = ['C0', 'C1', 'C2', 'C3']
    fig, ax = plt.subplots(figsize=FIG_SIZE)
    ind = np.arange(len(reports))

    bars = plt.bar(ind, data)
    #ax.set_title('Percentage of unit tested commits in each category', fontsize=TITLE_SIZE)
    ax.set_xticks(ind)
    ax.set_xticklabels(reports.keys(), fontsize=XLAB_SIZE)
    ax.set_ylabel("Unit Tested Ratio", fontsize=YLAB_SIZE)
    ax.tick_params(labelsize=TICK_SIZE)

    for c, b in enumerate(bars):
        height = b.get_height()
        b.set_facecolor(color[c])
        ax.text(b.get_x() + b.get_width()/2, 1.01 * height, '{}'.format(num_tested[c]), fontsize=BAR_NUM_SIZE)

    image_name = res_dir + '/' + 'utestratio_vs_class.png'
    plt.savefig(image_name)
    plt.close()


def plot_lines_modified(res_dir, reports):
    data = [r.lines_modified() for r in reports.values()]

    fig, ax = plt.subplots(figsize=FIG_SIZE)

    bp = ax.boxplot(data)
    #ax.set_title('LOC modified for commits in each category', fontsize=TITLE_SIZE)
    ax.set_xticklabels(reports.keys(), fontsize=XLAB_SIZE)
    ax.set_ylabel("Modified LOC", fontsize=YLAB_SIZE)
    ax.tick_params(labelsize=TICK_SIZE)

    image_name = res_dir + '/' + 'locmod_vs_class.png'
    plt.savefig(image_name)
    plt.close()


def plot_lines_removed(res_dir, reports):
    data = [r.lines_removed() for r in reports.values()]

    fig, ax = plt.subplots(figsize=FIG_SIZE)

    bp = ax.boxplot(data)
    #ax.set_title('LOC removed for commits in each category', fontsize=TITLE_SIZE)
    ax.set_xticklabels(reports.keys(), fontsize=XLAB_SIZE)
    ax.set_ylabel("Removed LOC", fontsize=YLAB_SIZE)
    ax.tick_params(labelsize=TICK_SIZE)

    image_name = res_dir + '/' + 'locrm_vs_class.png'
    plt.savefig(image_name)
    plt.close()


def plot_lines_added(res_dir, reports):
    data = [r.lines_added() for r in reports.values()]

    fig, ax = plt.subplots(figsize=FIG_SIZE)

    bp = ax.boxplot(data)
    #ax.set_title('LOC added for commits in each category', fontsize=TITLE_SIZE)
    ax.set_xticklabels(reports.keys(), fontsize=XLAB_SIZE)
    ax.set_ylabel("Added LOC", fontsize=YLAB_SIZE)
    ax.tick_params(labelsize=TICK_SIZE)

    image_name = res_dir + '/' + 'locadd_vs_class.png'
    plt.savefig(image_name)
    plt.close()


def clean_null(df):
    cleandf = df[df['final_category'].notnull()]
    cleandf = cleandf[cleandf['assigned_category'].notnull()]
    return cleandf


def pairwise_corr_plot(res_dir, df):
    attrs = ['lines_modified', 'lines_added', 'lines_removed', 'num_comments', 'num_revisions',
             'upload_push_timediff']

    scatter_matrix(df[attrs], figsize=FIG_SIZE)
    image_name = res_dir + '/' + 'pairwise_scatter.png'
    plt.savefig(image_name)
    plt.close()


def format_ax_lab(key, unit):
    if key not in COL_MAP:
        print('Error: %s not in column name mapping' % key)
        return key
    key_explain = COL_MAP[key]
    if unit == '':
        return key_explain
    return "{} ({})".format(key_explain, unit)


def scatter_plot(res_dir, key1, unit1, key2, unit2, df):
    fig, ax = plt.subplots(figsize=FIG_SIZE)
    ax.scatter(df[key1], df[key2])
    xlab = format_ax_lab(key1, unit1)
    ylab = format_ax_lab(key2, unit2)
    ax.set_xlabel(xlab, fontsize=XLAB_SIZE)
    ax.set_ylabel(ylab, fontsize=YLAB_SIZE)
    ax.tick_params(labelsize=TICK_SIZE)

    image_name = res_dir + '/' + '_'.join([key1, key2]) + '.png'
    plt.savefig(image_name)
    plt.close()


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


def plot_ifunittested_timediff(res_dir, reports):
    assert(reports is not None and len(reports) != 0)
    data = [r.upush_timediff() for r in reports.values()]

    fig, ax = plt.subplots(figsize=FIG_SIZE)

    bp = ax.boxplot(data)
    #ax.set_title('time span from upload to push for unittested and non-unittested commits', fontsize=TITLE_SIZE)
    labels = [UTEST_MAP[k] for k in reports.keys()]
    ax.set_xticklabels(labels, fontsize=XLAB_SIZE)
    ax.set_ylabel("Time in Review (days)", fontsize=YLAB_SIZE)
    ax.tick_params(labelsize=TICK_SIZE)

    image_name = res_dir + '/' + 'timediff_vs_utest.png'
    plt.savefig(image_name)
    plt.close()


def plot_ifunittested_num_comments(res_dir, reports):
    assert(reports is not None and len(reports) != 0)
    data = [r.num_comments() for r in reports.values()]

    fig, ax = plt.subplots(figsize=FIG_SIZE)

    bp = ax.boxplot(data)
    #ax.set_title('Number of comments for unittested and non-unittested commits', fontsize=TITLE_SIZE)
    labels = [UTEST_MAP[k] for k in reports.keys()]
    ax.set_xticklabels(labels, fontsize=XLAB_SIZE)
    ax.set_ylabel("Code Review Comments", fontsize=YLAB_SIZE)
    ax.tick_params(labelsize=TICK_SIZE)

    image_name = res_dir + '/' + 'comments_vs_utest.png'
    plt.savefig(image_name)
    plt.close()


def plot_ifunittested_num_revisions(res_dir, reports):
    assert(reports is not None and len(reports) != 0)
    data = [r.num_revisions() for r in reports.values()]

    fig, ax = plt.subplots(figsize=FIG_SIZE)

    bp = ax.boxplot(data)
    #ax.set_title('Number of revisions for unittested and non-unittested commits', fontsize=TITLE_SIZE)
    labels = [UTEST_MAP[k] for k in reports.keys()]
    ax.set_xticklabels(labels, fontsize=XLAB_SIZE)
    ax.set_ylabel("Revisions", fontsize=YLAB_SIZE)
    ax.tick_params(labelsize=TICK_SIZE)

    image_name = res_dir + '/' + 'revisions_vs_utest.png'
    plt.savefig(image_name)
    plt.close()


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


def get_scatter_plots(res_dir, df):
    pairwise_corr_plot(res_dir, df)

    scatter_plot(res_dir, 'lines_modified', 'LOC', 'num_comments', '', df)
    scatter_plot(res_dir, 'lines_modified', 'LOC', 'num_revisions', '', df)
    scatter_plot(res_dir, 'lines_modified', 'LOC', 'upload_push_timediff', 'days', df)
    scatter_plot(res_dir, 'lines_added', 'LOC', 'upload_push_timediff', 'days', df)
    scatter_plot(res_dir, 'lines_added', 'LOC', 'num_comments', '', df)
    scatter_plot(res_dir, 'num_revisions', '', 'upload_push_timediff', 'days', df)
    scatter_plot(res_dir, 'num_comments', '', 'upload_push_timediff', 'days', df)
    scatter_plot(res_dir, 'num_comments', '', 'num_revisions', '', df)
    return


def get_class_plots(res_dir, df):
    reports = to_category_reports(df)

    # box plot for num_revisions for each category
    plot_num_revisions(res_dir, reports)
    # box plot for upload -> push timediff
    plot_upload_push_timediff(res_dir, reports)
    # bar chart for unittest ratio
    plot_unittest_ratio(res_dir, reports)
    # lines_modified for each category
    plot_lines_modified(res_dir, reports)
    plot_lines_added(res_dir, reports)
    plot_lines_removed(res_dir, reports)
    return


def get_unit_plots(res_dir, df):
    reports = get_unittested_vs_non(df)
    # upload_push_timediff vs. unittested/non_unittested
    plot_ifunittested_timediff(res_dir, reports)
    # num_comments vs. unittested/non_unittested
    plot_ifunittested_num_comments(res_dir, reports)
    # num_revisions vs. unittested/non_unittested
    plot_ifunittested_num_revisions(res_dir, reports)
    return


def plot_orig_category(res_dir, df):
    assign_cats = df['assigned_category'].value_counts()
    cat_index = assign_cats.index
    data = [assign_cats.loc[c] for c in cat_index]

    color = ['C0', 'C1', 'C2', 'C3', 'C4']
    color = color[0:len(assign_cats)]

    fig, ax = plt.subplots(figsize=FIG_SIZE)
    ind = np.arange(len(assign_cats))

    bars = plt.bar(ind, data)
    #ax.set_title('Number of issue reports in each assigned category', fontsize=TITLE_SIZE)
    ax.set_xticks(ind)
    ax.set_xticklabels(cat_index, fontsize=XLAB_SIZE)
    ax.set_ylabel("Issue Reports", fontsize=YLAB_SIZE)
    ax.tick_params(labelsize=TICK_SIZE)

    for c, b in enumerate(bars):
        height = b.get_height()
        b.set_facecolor(color[c])
        ax.text(b.get_x() + b.get_width() / 2, 1.01 * height, '{}'.format(height), fontsize=BAR_NUM_SIZE)

    image_name = res_dir + "/" + "assigned_cat.png"
    plt.savefig(image_name)
    plt.close()
    return


def plot_misclass_for(cat, right_class, mis_class, res_dir):
    mis_values = mis_class['final_category'].value_counts()
    right_values = right_class['final_category'].value_counts()
    right_name = right_values.index.tolist()[0]
    cat_index = mis_values.index.tolist()
    cat_index.append(right_name)
    cat_index.sort()

    series = pd.concat([right_values, mis_values])
    raw_counts = [series.loc[i] for i in cat_index]
    total_counts = sum(raw_counts)
    perc = [c/total_counts for c in raw_counts]

    fig, ax = plt.subplots(figsize=FIG_SIZE)
    ind = np.arange(len(cat_index))

    color = ['C0', 'C1', 'C2', 'C3', 'C4']
    color = color[0:len(cat_index)]

    # horizontal bar
    bars = plt.barh(ind, perc)
    #ax.set_title('Reports originally filled as {}'.format(cat), fontsize=TITLE_SIZE)
    ax.set_yticks(ind)
    ax.set_yticklabels(cat_index, fontsize=YLAB_SIZE)
    ax.set_xlabel("Classification Ratio", fontsize=XLAB_SIZE)
    ax.tick_params(labelsize=TICK_SIZE)

    for c, b in enumerate(bars):
        width = b.get_width()
        b.set_facecolor(color[c])
        ax.text(width * 1.01, c, '%d' % raw_counts[c], fontsize=BAR_NUM_SIZE)
    image_name = res_dir + "/" + cat + "_misclass_cat.png"
    plt.savefig(image_name)
    plt.close()


def plot_misclassification(res_dir, df):
    assign_cats_index = df['assigned_category'].value_counts().index
    reports = {}
    for cat in assign_cats_index:
        reports[cat] = to_reports('assigned_category', cat, df)
        right_class, mis_class = reports[cat].report_misclass(CAT_MAP)
        if right_class is None or mis_class is None:
            print('Warning: skipping %s due to missing mapping' % cat)
            continue
        right_perc = right_class.size / (right_class.size + mis_class.size)
        mis_perc = mis_class.size / (right_class.size + mis_class.size)
        print('For %s, %.4f were correctly classified' % (cat, right_perc))
        print('\t %.4f were incorrectly classified' % (mis_perc))
        plot_misclass_for(cat, right_class, mis_class, res_dir)


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
    agree_perc, unique_reports = get_rater_relibility(df)
    print('Percentage of agreement: %.4f' % agree_perc)

    # ====== START ANALYSIS ======
    # get original distribution of assigned feature
    plot_orig_category(args.res_dir, unique_reports)

    # get mis-classifications
    plot_misclassification(args.res_dir, unique_reports)

    # scatter plot
    get_scatter_plots(args.res_dir, df)

    # distribution across manual classification category
    get_class_plots(args.res_dir, df)

    # distribution in unit test vs not unit tested
    get_unit_plots(args.res_dir, df)

    # get box plots
    #for col in BOX_COLUMNS:
    #    if col not in df.columns:
    #        print('Error: requested column "%s" not in data' % col)
    #        continue
    #    make_box_plots(args.res_dir, df[col])


if __name__ == '__main__':
    main()
