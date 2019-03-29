#!/bin/bash

# get change id from a commit hash
# usage: bash get_changeid.sh HASH REPO_PATH
hash="$1"
repo="$2"
cd "$repo"
git show "$hash" | grep "Change-Id"

