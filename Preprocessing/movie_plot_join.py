import json
import pandas as pd

if __name__ == '__main__':

    scripts_urls = json.load(open('tmdb_matched_scripts_urls.json'))
    cmu = pd.read_csv('../Data/MovieSummaries/plot_summaries.txt',delimiter='\t',header=None)
    mpst = pd.read_csv('../Data/MovieSummaries/mpst_full_data.csv')
    wiki = pd.read_csv('../Data/MovieSummaries/wiki_movie_plots_deduped.csv')
    wiki_id2tmdb_id = json.load(open('../Data/tmdb_resources/wikipedia_id2tmdb_id.json'))
    cmu2tmdb = json.load(open('../Data/tmdb_resources/cmu_exist_tmdb_id2detail.json'))
    tmdb_id2detail = json.load(open('../Data/tmdb_resources/tmdb_id2detail_imdb_rating.json'))
    target_tmdb_ids = [m['tmdb_id'] for m in scripts_urls if 'tmdb_id' in m]
    tmdb_id2plot = {}

    # 1. mpst
    imdb_id2plot = {x['imdb_id']:x['plot_synopsis'] for _,x in mpst.iterrows()}
    cnt = 0

    for tmdb_id in tmdb_id2detail.keys():
        imdb_id = tmdb_id2detail[str(tmdb_id)]['imdb_id']
        if imdb_id in imdb_id2plot:
            tmdb_id2plot[tmdb_id] = imdb_id2plot[imdb_id]
            cnt += 1
    print(f"valid matching by mpst: {cnt}")

    # 2. cmu
    wiki_id2plot = {x[0]:x[1] for _,x in cmu.iterrows()}
    tmdb_id2wiki_id = {v:k for k,v in wiki_id2tmdb_id.items()}
    wiki_id2tmdb_id
    cnt = 0
    for tmdb_id, wiki_id in tmdb_id2wiki_id.items():
        if int(wiki_id) in wiki_id2plot:
            cnt += 1
            if tmdb_id in tmdb_id2plot:
                if len(tmdb_id2plot[tmdb_id]) > len(wiki_id2plot[int(wiki_id)]): # to keep shorter plot
                    tmdb_id2plot[tmdb_id] = wiki_id2plot[int(wiki_id)]
            else:
                tmdb_id2plot[tmdb_id] = wiki_id2plot[int(wiki_id)]
    print(f"valid matching by cmu: {cnt}")
    print(f"union to mpst is : {len(list(tmdb_id2plot.keys()))}")

    # 3. wiki
    remain_ids = [tmdb_ids for tmdb_ids in tmdb_id2detail.keys() if tmdb_ids not in tmdb_id2plot]
    cnt = 0
    title2plots = {x['Title'].lower():x['Plot'] for _,x in wiki.iterrows()}
    for tmdb_id in remain_ids:
        movie_title = tmdb_id2detail[str(tmdb_id)]['original_title']
        if movie_title.lower() in title2plots:
            tmdb_id2plot[tmdb_id] = title2plots[movie_title.lower()]
            cnt += 1

    print(f"additional backups from wiki data : {cnt}")
    print(f"We have total : {len(list(tmdb_id2plot.keys()))}")

    json.dump(tmdb_id2plot,open('tmdb_id2plot.json','w'))