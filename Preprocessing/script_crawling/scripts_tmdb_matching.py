from pathlib import Path
from tqdm import tqdm
from urllib.parse import quote, unquote
import pandas as pd
import json
import requests
import threading
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import string

import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import string
nltk.download('punkt')

token = os.environ['TMDB_token']
def fetch_movie_data(movie_name):
    url = f"https://api.themoviedb.org/3/search/movie?query={movie_name}&page=1"
    headers = {
        "accept": "application/json",
        "Authorization": token
    }
    response = requests.get(url, headers=headers)
    try:
        res_json = json.loads(response.text)
        return res_json
    except json.decoder.JSONDecodeError:
        movie2response[row.name] = {}
        return {}
    

def overlap_percentage(sentence1, sentence2):
    stop_words = set(stopwords.words('english'))
    words1 = word_tokenize(sentence1)
    words2 = word_tokenize(sentence2)
    words1 = [word.lower() for word in words1 if word.isalpha() and word.lower() not in stop_words]
    words2 = [word.lower() for word in words2 if word.isalpha() and word.lower() not in stop_words]

    total_unique_words = len(set(words1 + words2))
    overlap_count = len(set(words1) & set(words2))
    return overlap_count >= total_unique_words / 3

if __name__ == '__main__':
    manual_matching = json.load(open('manual_matching.json')) # handcrafted feature. Was so painful..
    scripts_urls = json.load(open('scripts_urls.json'))
    for movie_meta in tqdm(scripts_urls):
        movie_name = movie_meta['movie_name_url'].split('/')[-1].replace('%20Script.html','')
        res = fetch_movie_data(movie_name)
        if res:
            movie_meta['res'] = res

    for i,movie_meta in enumerate(scripts_urls):
        if i in manual_matching:
            movie_meta['tmdb_id']= manual_matching[i]
            continue
        movie_name = unquote(movie_meta['movie_name_url'].split('/')[-1].replace('%20Script.html',''))
        if movie_name.endswith(', The'):
            movie_name = 'The ' + movie_name[:-5]
        candidates = movie_meta['res']['results']
        for c in candidates:
            c['invalid'] = False
        if 'release_date' in movie_meta:
            # match if year and month are same.
            yy,mm = movie_meta['release_date'].split('.')
            flag = 0 # number of exact matching movie
            candi_id = -1
            for x in candidates:
                if 'release_date' in x and x['release_date']:
                    if x['release_date'].split('-')[0] != yy:
                        x['invalid'] = True
                    if '-' in x['release_date'] and x['release_date'].startswith(f'{yy}-{mm}'):
                        if flag:
                            flag += 1
                        if not flag:
                            if overlap_percentage(movie_name.lower(), x['title'].lower()):
                                flag = 1
                                candi_id = x['id']
            if flag == 1:
                movie_meta['tmdb_id'] = candi_id
                continue
        elif 'script_date' in movie_meta:
            yy,mm = movie_meta['script_date'].split('.')
            after_3_years = []
            for x in candidates:
                if not x['release_date']:
                    continue
                target_y = x['release_date'].split('-')[0]
                if len(x['release_date'].split('-')) == 1:
                    if int(target_y) < int(yy) or int(target_y) > int(yy) + 3:
                        x['invalid'] = True
                else:
                    target_m = x['release_date'].split('-')[1]
                    if int(target_y) == int(yy) and int(target_m) < int(mm):
                        x['invalid'] = True
        for c in candidates:
            if not overlap_percentage(movie_name.lower(), c['title'].lower()):
                c['invalid'] = True
        valid_candidates = [c for c in candidates if c['invalid'] == False]
        if len(valid_candidates) == 1:
            if movie_name.lower() == valid_candidates[0]['title'].lower():
                movie_meta['tmdb_id'] = valid_candidates[0]['id']
            else:
                if overlap_percentage(movie_name.lower(), valid_candidates[0]['title'].lower()):
                    movie_meta['tmdb_id'] = valid_candidates[0]['id']
        elif len(valid_candidates) > 1:
            # if exact name matchs are more than 1 and top popularity overwhelms others, select it.
            exacts = [c for c in candidates if c['title'].lower() == movie_name.lower()]
            exacts.sort(key=lambda x:-x['popularity'])
            if (len(exacts) > 1 and exacts[0]['popularity'] > exacts[1]['popularity'] * 4) or (len(exacts) == 1 and exacts[0]['popularity'] > 25):
                movie_meta['tmdb_id'] = exacts[0]['id']

    json.dump(scripts_urls, open('tmdb_matched_scripts_urls.json','w')) # total 1060 sample matched.