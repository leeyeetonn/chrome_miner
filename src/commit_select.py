#!/bin/env python
import csv
import random
import re
import sys

# Commits should be grabbed like this and dumped to a file:
# git log --after="2017-09-01" --until="2018-09-01" --date=short --pretty=full

def main(argv):
    """ Randomly select a subset of commits.

    Given a list of commits, parse them, then randomly select a subset and
    output these to a file.

    Args:
        argv: number of commits, input file, output file
    """
    if len(argv) < 4:
        print("usage: commit_select <num commits> <input file> <output file>")
        raise ValueError

    num_commits = int(argv[1])
    commit_file = argv[2]
    output_file = argv[3]
    commits = []

    with open(commit_file, 'r') as f:
        commit = {}
        for line in f.readlines():
            if re.match('commit ', line) is not None:
                if bool(commit) and None not in commit.values():
                    commits.append(commit)
                    commit = {}
                commit['hash'] = line.split(' ')[1].split()[0]
                commit['date'] = None
                commit['bug'] = None
                commit['review'] = None
            if re.match('Date:\s+', line) is not None:
                commit['date'] = line.split()[1].split()[0]
            if re.match('\s+BUG=chromium:', line) is not None:
                # This is buggy if a commit references more than one issue, just
                # fix these manually
                bug_id = line.split('BUG=chromium:')[1].split()[0]
                commit['bug'] = 'crbug.com/' + bug_id
            if re.match('\s+Reviewed-on: ', line) is not None:
                commit['review'] = line.split('Reviewed-on: ')[1].split()[0]
        if bool(commit) and None not in commit.values():
            commits.append(commit)

    # Select all of them if the user wants more than we have
    num_commits = min(num_commits, len(commits))

    # Set a seed for reproducability
    random.seed(11235)
    random.shuffle(commits)
    commits = commits[:num_commits]

    with open(output_file, "w", newline='') as f:
        writer = csv.DictWriter(f, commits[0].keys())
        writer.writeheader()
        for c in commits:
            writer.writerow(c)

if __name__ == "__main__":
    """
    Main method
    """
    main(sys.argv)

