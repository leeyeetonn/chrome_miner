import argparse
import os
import json
import pandas as pd
import subprocess
import re
import requests
from contextlib import contextmanager
from urllib.parse import quote

UP_ENG_FOLDER = 'aosp/platform/system/update_engine'
PLATFORM2_FOLDER = 'chromiumos/platform/system_api'
URL_PREFIX = 'https://chromium-review.googlesource.com/changes'

def test_fexist(fpath):
    if os.path.exists(fpath):
        return True
    print('Error: Given file %s not found.' % fpath)
    return False


def parse_cmit_list(inpath):
    assert(test_fexist(inpath))
    # read input file as pandas dataframe
    df = pd.read_csv(inpath)
    assert(df is not None)

    # get hash for each commit
    cmit_list = df['hash'].values
    return cmit_list, df


@contextmanager
def cd(newdir):
    prevdir = os.getcwd()
    os.chdir(os.path.expanduser(newdir))
    try:
        yield
    finally:
        os.chdir(prevdir)


def do_git_show(repo, cmit_hash):
    with cd(repo):
        cmd = ['git', 'show', '--pretty=tformat:', '--numstat', cmit_hash]
        cp = subprocess.run(cmd, capture_output=True, universal_newlines=True)
        if cp.returncode != 0:
            print('Warning: extract stat from commit %s failed' % cmit_hash)
            return
        outline = cp.stdout.rstrip('\n').replace('\n', '\t').split('\t')
        return outline


def get_changed_fnames(repo, cmit_hash):
    with cd(repo):
        cmd = ['git', 'show', '--pretty=format:', '--name-only', cmit_hash]
        cp = subprocess.run(cmd, capture_output=True, universal_newlines=True)
        if cp.returncode != 0:
            print('Warning: extract unit test from commit %s failed' % cmit_hash)
            return
        outline = cp.stdout.rstrip('\n').split('\n')
        return outline


def get_change_id(repo, cmit_hash):
    cmd = ['bash', 'get_changeid.sh', cmit_hash, repo]
    cp = subprocess.run(cmd, capture_output=True, universal_newlines=True)
    if cp.returncode != 0:
        print('Warning: extract changeid from commit %s failed' % cmit_hash)
        print(cp)
        return

    # may have multiple change id
    changeid_toks = cp.stdout.rstrip('\n').split('\n')
    # only take the first one
    changeid = changeid_toks[0].split(':')[1].replace(' ', '')
    #print('--- changeid = ', changeid)
    return changeid


def calc_stat(stat_list):
    li_len = len(stat_list)
    added = 0
    deled = 0
    for add_ind in range(0, li_len, 3):
        del_ind = add_ind + 1
        # special case for binary file change
        if stat_list[add_ind] == '-' or stat_list[del_ind] == '-':
            continue

        added += int(stat_list[add_ind])
        deled += int(stat_list[del_ind])

    return added, deled


def build_query(repo, changeid, target):
    if re.search('.*update_engine.*', repo):
        url = quote(UP_ENG_FOLDER, safe='')
    elif re.search('.*platform2.*', repo):
        url = quote(PLATFORM2_FOLDER, safe='')
    else:
        print('Error: unknown choice %s' % repo)
        exit(1)

    # construct query
    query = URL_PREFIX + '/' + url + '~master~' + changeid + '/' + target
    return query


def proc_query(query):
    r = requests.get(query)
    if r.status_code != requests.codes.ok:
        print('Error: query failed with status %d' %r.status_code)
        print('Please inspect query: [%s]' % query)
        return None

    # r.text has )]}' in the beginning causing failures to json decoder
    # !!WORKAROUND: remove these chars from string and use json loads
    res_txt = r.text[5:]
    res_json = json.loads(res_txt)
    return res_json


def extract_from_messages(injson):
    stats = {}
    json_len = len(injson)
    stats['num_msg'] = json_len

    # first message
    fst_msg = injson[0]
    stats['submit_time'] = fst_msg['date']

    # get the last message
    last_msg = injson[json_len - 1]
    stats['num_revision'] = last_msg['_revision_number'] - 1
    stats['push_time'] = last_msg['date']

    # get the time to plus2
    for msg in injson:
        # possible to have multiple Code-Review+2, only take the last one
        if re.search('.*Code-Review\+2.*', msg['message']):
            stats['plus_2'] = msg['date']
    return stats


def check_reply(cm, heads, non_start):
    if "in_reply_to" not in cm: # head of a comment chain
        comment_chain = {cm['id'] : cm['unresolved']}
        heads.append(comment_chain)
    else:
        non_flag = False
        replied_id = cm['in_reply_to']
        for hd in heads:
            if replied_id in hd:
                tail = cm['id']
                hd[replied_id] = tail
                hd[tail] = cm['unresolved']
                non_flag = True
                break
        if non_flag is False and cm not in non_start:
            non_start.append(cm)    # `cm` is a reply message but the head hasn't be dded to `heads`


def extract_from_comments(injson):
    stats = {}
    non_start = []
    heads = []
    for _, v in injson.items():
        for cm in v:
            check_reply(cm, heads, non_start)

    while len(non_start) != 0:
        n = non_start.pop(0)
        check_reply(n, heads, non_start)

    # count True in `heads` to get unresolved comments
    num_unresolved = 0
    for hd in heads:
        if True in hd.values():
            num_unresolved += 1

    stats['unresolved'] = num_unresolved
    return stats


def extract_stats(injson, target):
    assert(injson is not None or len(injson) != 0)
    if target == 'messages':
        return extract_from_messages(injson)
    elif target == 'comments':
        return extract_from_comments(injson)


def get_gerrit_stat(repo, cmit, changeid):
    targets = ['messages', 'comments']
    gerrit_stats = {}
    for t in targets:
        query = build_query(repo, changeid, t)

        # get response from gerrit
        res_json = proc_query(query)
        if res_json is None:
            continue

        # extract num_revision, num_comments, time_to_plus2, time_submitted, time_pushed
        stats = extract_stats(res_json, t)

        # will override if key overlaps, but no overlap expected
        gerrit_stats.update(stats)

    return gerrit_stats


def get_unit_test(fnames):
    assert(fnames is not None)
    test_flag = False
    nontest_flag = False

    for f in fnames:
        if re.search('.*unittest.*', f):
            test_flag = True
        else:
            nontest_flag = True

    is_unittested = False
    is_unittest = False
    if test_flag and nontest_flag:
        is_unittested = True
    elif test_flag and not nontest_flag:
        is_unittest = True

    return is_unittested, is_unittest


def main():
    parser = argparse.ArgumentParser(description='Take input commits and get related stats')
    parser.add_argument('infile', type=str, help='input file path containing the list of commits sha')
    parser.add_argument('repo', type=str, help='path to the git repo')
    parser.add_argument('outfile', type=str, help='output filename')
    args = parser.parse_args()

    cmit_list, df = parse_cmit_list(args.infile)

    added_loc_list = []
    del_loc_list = []
    num_msg_list = []
    t_submit_list = []
    t_push_list = []
    num_revision_list = []
    t_plus2_list = []
    num_unresolved_list = []
    is_unittested_list = []
    is_unittest_list = []
    for index, cmit in enumerate(cmit_list):
        stat_list = do_git_show(args.repo, cmit)
        added_loc, del_loc = calc_stat(stat_list)
        added_loc_list.append(added_loc)
        del_loc_list.append(del_loc)

        # unit test related
        files_changed = get_changed_fnames(args.repo, cmit)
        is_unittested, is_unittest = get_unit_test(files_changed)
        is_unittested_list.append(is_unittested)
        is_unittest_list.append(is_unittest)

        # get changeid from commit
        changeid = get_change_id(args.repo, cmit)

        # extract gerrit related stats
        gerrit_stats = get_gerrit_stat(args.repo, cmit, changeid)
        if len(gerrit_stats) == 0:
            # query to gerrit failed, fill -1 for placeholder
            num_msg_list.append(-1)
            t_submit_list.append(-1)
            t_push_list.append(-1)
            num_revision_list.append(-1)
            t_plus2_list.append(-1)
            num_unresolved_list.append(-1)
        else:
            num_msg_list.append(gerrit_stats['num_msg'])
            t_submit_list.append(gerrit_stats['submit_time'])
            t_push_list.append(gerrit_stats['push_time'])
            num_revision_list.append(gerrit_stats['num_revision'])
            t_plus2_list.append(gerrit_stats['plus_2'])
            num_unresolved_list.append(gerrit_stats['unresolved'])

    df['lines_added'] = added_loc_list
    df['lines_removed'] = del_loc_list
    df['num_msg'] = num_msg_list
    df['time_uploaded'] = t_submit_list
    df['time_pushed'] = t_push_list
    df['time_plus2'] = t_plus2_list
    df['num_revisions'] = num_revision_list
    df['num_unresolved_comments'] = num_unresolved_list
    df['is_unittested'] = is_unittested_list
    df['is_unittest_only'] = is_unittest_list

    # finished getting added LOC and removed LOC
    df.to_csv(args.outfile)


if __name__ == '__main__':
    main()
