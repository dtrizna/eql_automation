from elasticsearch import Elasticsearch
from elasticsearch.client import EqlClient
import argparse
import json
import time
import ast
import logging

def wait_for_completion(eql, id, verbose=True):
    """Function takes EQL client object and ID of already running job, then informs when job is done.

    Args:
        eql (elasticsearch.client.EqlClient): instantiated EQL client.
        id (str): Sting representing ID of an EQL job (returned by eql.search() method) 
        verbose (bool, optional): Defaults to True.

    Returns:
        dict: JSON dict with EQL client reponse on job status.
    """
    i = 1
    res = eql.get_status(id)
    while res["is_running"]:
            res = eql.get_status(id)
            time.sleep(5)
            if verbose:
                print(f" [*] {time.ctime()}: Waiting for {id} completion: {i*5}s", end="\r")
                i += 1
    status = eql.get_status(id)
    if status["completion_status"] == 200:
            
            logging.warning(f" [+] {time.ctime()}: {id} succeded..")
            return status
    else:
            logging.warning(f" [-] {time.ctime()}: {id} failed..")
            return status


def launch_eql(es, index_pattern, query, mode, output, verbose=True):
    """Main function that takes an index pattern and actual EQL query and performs results acquisition.

    Args:
        es (elasticsearch.Elasticsearch): elasticsearch-py main client object
        index_pattern (str): pattern representing indices to query within elastic, takes wildcards, e.g. "winlogbeat-2021.12.0*"
        query (dict): dictionary object representing valid EQL search API body
        verbose (bool, optional): Defaults to True.

    Returns:
        dict: dictionary with keys as indices and values as JSON results of EQL query
    """
    eql = EqlClient(es)
    indices_raw = es.cat.indices(index_pattern).strip().split("\n")
    logging.warning(f" [+] {time.ctime()}: Total indices to query: {len(indices_raw)}")
    running = {}
    results = {}

    for index in indices_raw:
            index = index.split()[2]
            res = eql.search(index, query, wait_for_completion_timeout="1s")
            if res["is_running"]:
                    logging.warning(f" [+] {time.ctime()}: Instantiated job for {index} and running in background with job ID: {res['id']}")
                    
                    if mode == "sequential":
                        wait_for_completion(eql, res["id"], verbose=verbose)
                        
                        results = eql.get(res["id"])
                        result_file = output+"_"+index+".json"
                        logging.warning(f" [+] {time.ctime()}: Results acquired for {index}. Saved to: {result_file}")
                        json.dump(results, open(result_file, "w"), indent=4)
                    else:
                        running[index] = res["id"]
            else:
                result_file = output+"_"+index+".json"
                logging.warning(f" [+] {time.ctime()}: Results acquired for {index}. Saved to: {result_file}")
                json.dump(res, open(result_file, "w"), indent=4)

    if mode == "parallel":
        for index in running:
                job_id = running[index]
                wait_for_completion(eql, job_id, verbose=verbose) 
                results = eql.get(job_id)
                
                result_file = output+"_"+index+".json"
                logging.warning(f" [+] {time.ctime()}: Results acquired for {index}. Saved to: {result_file}")
                json.dump(results, open(result_file, "w"), indent=4)
        


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Execute EQL queries and save output to a JSON file")
    
    # elastic arguments
    parser.add_argument("--API_KEY", required=True, help="JSON file with API key to Elastic, containing 'id', 'name', 'api_key' values.")
    parser.add_argument("--ES_URL", default="https://example.com:9200/")
    parser.add_argument("--index", required=True, help="Index pattern to execute EQL query against, e.g. \"winlogbeat-2021.12.0*\"")
    
    # file arguments
    parser.add_argument("--query-file", required=True, help="Path to file with query representing valid EQL search API body.")
    parser.add_argument("--output", default="out", help="Where to store results of EQL query")

    # execution mode    
    parser.add_argument("--mode", choices=["sequential", "parallel"], default="parallel", help="Whether to execute EQL queries sequentially over indices or in parallel")

    # logging arguments
    parser.add_argument("-v", "--verbose", action="store_true")
    parser.add_argument("-d", "--debug", action="store_true")
    parser.add_argument("--logfile", type=str, help="File to store logging messages")

    args = parser.parse_args()
    
    level = logging.WARNING if args.verbose else logging.ERROR
    level = logging.DEBUG if args.debug else level # overwrite if want debug output
    
    # if logfile argument present - log to a file instead of stdout
    if args.logfile:
        logging.basicConfig(handlers=[logging.FileHandler(args.logfile, 'a', 'utf-8')], level=level)
    else:
        logging.basicConfig(level=level)
    
    # reading EQL query file
    with open(args.query_file) as f:
        query = f.read()
    query = ast.literal_eval(query)
    
    # elasticsearch-py instantiation
    API = json.load(open(args.API_KEY))
    es = Elasticsearch(args.ES_URL, api_key=(API["id"], API["api_key"]), timeout=360)
    logging.warning(f" [!] {time.ctime()}: Elastic status check: {es.cat.health().strip()}")
    
    logging.warning(f" [!] {time.ctime()}: Running in {args.mode} mode!")
    launch_eql(es, args.index, query, args.mode, args.output, args.verbose)

    
