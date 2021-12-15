# Automation and handling of complex EQL queries

This logic allows to execute complex EQL queries against multiple indices either in `sequential` (one EQL query per index at a time for low capacity elastic clusters) of `parallel` (execute queries against all indices behind pattern and collect results) manner.

## Usage
```
usage: execute_eql.py [-h] --API_KEY API_KEY [--ES_URL ES_URL] --index INDEX --query-file QUERY_FILE [--output OUTPUT] [--mode {sequential,parallel}] [-v] [-d] [--logfile LOGFILE]

Execute EQL queries and save output to a JSON file

optional arguments:
  -h, --help            show this help message and exit
  --API_KEY API_KEY     JSON file with API key to Elastic, containing 'id', 'name', 'api_key' values.
  --ES_URL ES_URL
  --index INDEX         Index pattern to execute EQL query against, e.g. "winlogbeat-2021.12.0*"
  --query-file QUERY_FILE
                        Path to file with query representing valid EQL search API body.
  --output OUTPUT       Where to store results of EQL query
  --mode {sequential,parallel}
                        Whether to execute EQL queries sequentially over indices or in parallel
  -v, --verbose
  -d, --debug
  --logfile LOGFILE     File to store logging messages
```

## Execution
```
% python3 execute_eql.py -v --API_KEY .my.api --ES_URL "https://example.com:9200/" \
                                            --index "winlogbeat-2021-12-0*" \
                                            --output test \
                                            --query-file eql_examples/simple.winlogbeat.eql

WARNING:root: [!] Wed Dec 15 13:07:37 2021: Elastic status check: 1639570058 12:07:38 my green 51 36 29790 14895 0 0 0 0 - 100.0%
WARNING:root: [!] Wed Dec 15 13:07:38 2021: Running in parallel mode!
WARNING:root: [+] Wed Dec 15 13:07:44 2021: Total indices to query: 10
WARNING:root: [+] Wed Dec 15 13:07:44 2021: Results acquired for winlogbeat-2021-12-01. Saved to: test_winlogbeat-2021-12-01.json
WARNING:root: [+] Wed Dec 15 13:07:45 2021: Results acquired for winlogbeat-2021-12-02. Saved to: test_winlogbeat-2021-12-02.json
WARNING:root: [+] Wed Dec 15 13:07:46 2021: Results acquired for winlogbeat-2021-12-03. Saved to: test_winlogbeat-2021-12-03.json
WARNING:root: [+] Wed Dec 15 13:07:47 2021: Results acquired for winlogbeat-2021-12-04. Saved to: test_winlogbeat-2021-12-04.json
WARNING:root: [+] Wed Dec 15 13:07:48 2021: Instantiated job for winlogbeat-2021-12-05 and running in background with job ID: FkE0Sk5UWUY4U3VDZ1RHLWk0NmNfVVEeQWhENk84aW9UcWVUQjBJUGtmbkNkUToxMDYyNjg2
WARNING:root: [+] Wed Dec 15 13:07:50 2021: Results acquired for winlogbeat-2021-12-06. Saved to: test_winlogbeat-2021-12-06.json
WARNING:root: [+] Wed Dec 15 13:07:50 2021: Results acquired for winlogbeat-2021-12-07. Saved to: test_winlogbeat-2021-12-07.json
WARNING:root: [+] Wed Dec 15 13:07:51 2021: Results acquired for winlogbeat-2021-12-08. Saved to: test_winlogbeat-2021-12-08.json
WARNING:root: [+] Wed Dec 15 13:07:52 2021: Results acquired for winlogbeat-2021-12-09. Saved to: test_winlogbeat-2021-12-09.json
WARNING:root: [+] Wed Dec 15 13:07:49 2021: Results acquired for winlogbeat-2021-12-00. Saved to: test_winlogbeat-2021-12-00.json
WARNING:root: [+] Wed Dec 15 13:07:52 2021: FkE0Sk5UWUY4U3VDZ1RHLWk0NmNfVVEeQWhENk84aW9UcWVUQjBJUGtmbkNkUToxMDYyNjg2 succeded..
WARNING:root: [+] Wed Dec 15 13:07:52 2021: Results acquired for winlogbeat-2021-12-05. Saved to: test_winlogbeat-2021-12-05.json
```