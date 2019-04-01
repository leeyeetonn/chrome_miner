# Mining ChromiumOS

### Dependency
1. python 3.7
2. pandas 0.24.2
3. requests 2.21.0
4. matplotlib 3.0.3
5. scipy 1.2.1


### Run Extraction
```sh
python src/get_stat.py <input_csv> <repo_path> <output_name>
```

### Run Analysis
```sh
python src/analyze_extracted.py data/all_commits_extracted.csv result
```
The generated box plots and aggregated data will be stored in `result` folder


### Table Legend
* see `table_legend` for descriptions of column names


### TODO
2. docker for reproducibility (probably unneeded, but a nice touch if we have time)
3. current stats are for selected bug fixing commits; 
4. colin - post code for commit parsing
find corresponding bug-introducing commit and get related stats
