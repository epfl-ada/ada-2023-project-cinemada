import requests
from bs4 import BeautifulSoup
import os
from urllib.parse import quote
from tqdm.notebook import tqdm
import json
from collections import defaultdict
import re
import pandas as pd


def extract_date(input_string):
    months = {
        "January": "01", "February": "02", "March": "03", "April": "04",
        "May": "05", "June": "06", "July": "07", "August": "08",
        "September": "09", "October": "10", "November": "11", "December": "12"
    }
    match = re.search(r'(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{4})', input_string)
    if match:
        month, year = match.groups()
        return f"{year}.{months[month]}"
    else:
        return ""
    
if __name__ == '__main__':
    url = 'https://imsdb.com/all-scripts.html'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    script_links = soup.find_all('a', href=True)  
    urls = [quote('https://imsdb.com' + x['href'],safe=':/') for x in script_links if x['href'].startswith('/Movie Scripts')]

    scripts_urls = []
    for movie_info_url in tqdm(urls):
        response_ex = requests.get(movie_info_url)
        soup_ex = BeautifulSoup(response_ex.text, 'html.parser')
        url_lists = soup_ex.find_all('a', href=lambda href: href and href.startswith('/scripts/'))
        if len(url_lists) ==0:
            continue
        script_url = url_lists[0]['href']
        movie_meta = {
            'movie_name_url': movie_info_url,
            'script_url': quote('https://imsdb.com' + script_url,safe=':/')
        }
        release_date = ''
        script_date = ''
        for i in str(soup_ex).split('\n'):
            if 'Movie Release Date' in i:
                release_date = extract_date(i)
            if 'Script Date' in i:
                script_date = extract_date(i)
        if release_date:
            movie_meta['release_date'] = release_date
        if script_date:
            movie_meta['script_date'] = script_date
        scripts_urls.append(movie_meta)


    json.dump(scripts_urls, open('scripts_urls.json','w'))