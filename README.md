# mining chromiumOS

### Dependency
1. python 3.7
2. pandas 0.24.2
3. requests 2.21.0


### Run
```sh
python get_stat.py <input_csv> <repo_path> <output_name>

```
### Table Legend
* see `table_legend` for descriptions of column names


### TODO
1. get data for is\_unittested and is\_unittest
2. docker for reproducibility
3. current stats are for selected bug fixing commits; 
find corresponding bug-introducing commit and get related stats
