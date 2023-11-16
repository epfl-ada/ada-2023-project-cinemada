import requests
import json
import pandas as pd
import os
import gzip
from pathlib import Path
from tqdm import tqdm
from urllib.parse import quote
import threading
import random

# You can get your API token from https://developer.themoviedb.org/docs
# token = <Your TMDB token>


def download_movid_ids(date_str="11_14_2023"):
    if not os.path.isdir('tmdb_resources'):
        os.mkdir('tmdb_resources')
    if os.path.isdir('tmdb_resources/movie_ids.jsonl'):
        pass
    url = f"http://files.tmdb.org/p/exports/movie_ids_{date_str}.json.gz"
    headers = {
        "accept": "application/json",
        "Authorization": token
    }
    response = requests.get(url, headers=headers)
    with open("tmdb_resources/movie_ids.json.gz", "wb") as f:
        f.write(response.content)
        
    with gzip.open("tmdb_resources/movie_ids.json.gz", "rb") as gz_file:
        with open("tmdb_resources/movie_ids.jsonl", "wb") as json_file:
            json_file.write(gz_file.read())
    os.remove("tmdb_resources/movie_ids.json.gz")
        
def download_people_ids(date_str="11_14_2023"):
    if not os.path.isdir('tmdb_resources'):
        os.mkdir('tmdb_resources')
    if os.path.isdir('tmdb_resources/people_ids.jsonl'):
        pass
    url = f"http://files.tmdb.org/p/exports/person_ids_{date_str}.json.gz"
    headers = {
        "accept": "application/json",
        "Authorization": token
    }
    response = requests.get(url, headers=headers)
    with open("tmdb_resources/people_ids.json.gz", "wb") as f:
        f.write(response.content)
        
    with gzip.open("tmdb_resources/people_ids.json.gz", "rb") as gz_file:
        with open("tmdb_resources/people_ids.jsonl", "wb") as json_file:
            json_file.write(gz_file.read())
    os.remove("tmdb_resources/people_ids.json.gz")
    

def fetch_detail(tmdb_id, tmdb_id2detail, lock):
    url = f"https://api.themoviedb.org/3/movie/{tmdb_id}?language=en-US"
    headers = {
        "accept": "application/json",
        "Authorization": token
    }
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        with lock:
            tmdb_id2detail[tmdb_id] = response.text


def fetch_credit(tmdb_id, tmdb_id2credit, lock):
    url = f"https://api.themoviedb.org/3/movie/{tmdb_id}/credits?language=en-US"
    headers = {
        "accept": "application/json",
        "Authorization": token
    }
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        with lock:
            tmdb_id2credit[tmdb_id] = response.text
        
def download_detail():
    movie_id_df = pd.read_json(path_or_buf='tmdb_resources/movie_ids.jsonl', lines=True)
    movie_ids = [ str(x) for x in movie_id_df['id'] ]
    data_path = 'tmdb_resources/tmdb_id2detail.json'
    if not os.path.exists(data_path):
        tmdb_id2detail = {}
    else:
        tmdb_id2detail = json.load(open(data_path,'r'))

    remain_movie_ids = list(set(movie_ids) - set(tmdb_id2detail.keys()))

    
    if not remain_movie_ids:
        print('detail datas are already prepared!')
        return tmdb_id2detail

    print(f'Existed : {len(tmdb_id2detail.keys())}\nLeft: {len(remain_movie_ids)}\n Start downloading.')
    random.shuffle(remain_movie_ids)
    lock = threading.Lock()
    threads = []
    for i,tmdb_id in tqdm(enumerate(remain_movie_ids),total=len(remain_movie_ids)):
        t = threading.Thread(target=fetch_detail, args=(tmdb_id, tmdb_id2detail, lock))
        threads.append(t)
        t.start()

        if len(threads) >= 15:
            threads[0].join()
            threads.pop(0)
            
        if i% 5000 == 4999:
            with lock:
                with open(data_path, 'w') as f:
                    json.dump(tmdb_id2detail, f)
                    print('progress saved')

    for t in threads:
        t.join()

    with open(data_path, 'w') as f:
        json.dump(tmdb_id2detail, f)
    return tmdb_id2detail

def download_credits(tmdb_id2detail):
    target_tmdb_id_list = [k for k,v in tmdb_id2detail.items() if json.loads(v)['budget'] > 0 and json.loads(v)['revenue'] > 0]
    
    data_path = 'tmdb_resources/tmdb_id2credit.json'
    tmdb_id2credit = json.load(open(data_path,'r')) if os.path.exists(data_path) else {}
    remain_movie_ids = list(set(target_tmdb_id_list) - set(tmdb_id2credit.keys()))
    
    print(f'Existed : {len(tmdb_id2credit.keys())}\nLeft: {len(remain_movie_ids)}\n Start downloading.')
    random.shuffle(remain_movie_ids)
    lock = threading.Lock()
    threads = []
    for i,tmdb_id in tqdm(enumerate(remain_movie_ids),total=len(remain_movie_ids)):
        t = threading.Thread(target=fetch_credit, args=(tmdb_id, tmdb_id2credit, lock))
        threads.append(t)
        t.start()

        if len(threads) >= 15:
            threads[0].join()
            threads.pop(0)
            
        if i% 5000 == 4999:
            with lock:
                with open(data_path, 'w') as f:
                    json.dump(tmdb_id2credit, f)
                    print('progress saved')

    for t in threads:
        t.join()

    with open(data_path, 'w') as f:
        json.dump(tmdb_id2credit, f)
    
if __name__ == '__main__':
#    tmdb_id2detail = download_detail()
    tmdb_id2detail = json.load(open('tmdb_resources/tmdb_id2detail.json','r'))
    download_credits(tmdb_id2detail)