import requests
from bs4 import BeautifulSoup
import os
from urllib.parse import quote


if __name__ == "__main__":
    scripts_urls= json.load(open('scripts_urls.json'))
    url2soup_obj = {}
    for name_url in tqdm(scripts_urls):
        url_ex = name_url['script_url'] 

        response_ex = requests.get(url_ex)
        if response_ex.status_code == 200:
            soup_ex = BeautifulSoup(response_ex.text, 'html.parser')
            url2soup_obj[url_ex] = soup_ex
    url2pairs = {}
    for name_url in tqdm(list(url2soup_obj.keys())):
        url_ex = name_url
        soup_ex = url2soup_obj[url_ex]
        raw_script = str(soup_ex).split('<table width="100%"><tr><td class="scrtext">')[1]
        clipped_script = raw_script.split("""<table align="center" border="0" cellpadding="5" cellspacing="0" class="body" style="BORDER-TOP: #000000 1px solid; BORDER-RIGHT: #000000 1px solid; BORDER-LEFT: #000000 1px solid; BORDER-BOTTOM: #000000 1px solid;" width="85%">""")[0]
        clipped_script = clipped_script.replace('\r','').replace('<br/>','\n').replace('\n</b>','</b>\n')
        lines = []
        for c in clipped_script.split('\n\n'):
            for l in c.split('\n'):
                lines.append(l)
        if any([True for _ in lines if '<b>' in _]):
            pair_list = []
            key = 'Title'
            buffer = []
            for i in lines:
                if '<b>' in i:
                    pair_list.append({key:' '.join(buffer)})
                    buffer = []
                    key = i.replace('<b>','').replace('<\b>','')
                else:
                    if i.replace('\r','').replace(' ','') != '':
                        buffer.append(i.strip())
            url2pairs[url_ex] = pair_list
        else:
            continue

    json.dump(url2pairs,open('url2pairs.json','w'))