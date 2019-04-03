# Mining ChromiumOS

### Dependency
1. python 3.7
2. pandas 0.24.2
3. requests 2.21.0
4. matplotlib 3.0.3
5. scipy 1.2.1


### Run Extraction
```sh
python get_stat.py <input_csv> <repo_path> <output_name>
```

### Run Analysis
```sh
python analyze_extracted.py ../data/all_commits_extracted.csv ../result
```
The generated box plots and aggregated data will be stored in `result` folder


### Table Legend
* see `table_legend` for descriptions of column names


### Get More Analysis Method
To develop more analysis method, add methods to `class IssueReport`.
This class can be used to separate different categories (i.e. BUG, RFE, etc.)
OR to separate `is_unittested = True` from `is_unittested = False`, etc.
