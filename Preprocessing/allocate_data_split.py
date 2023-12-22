import json
import random
from collections import defaultdict

if __name__ == '__main__':
    tmdb_id2matched_scripts = json.load(open('tmdb_id2matched_scripts.json'))
    tmdb_id2plot = json.load(open('tmdb_id2plot.json'))
    random.seed(1)
    tmdb_ids =  list(tmdb_id2matched_scripts.keys())
    tmdb_ids = sorted(tmdb_ids, key=lambda x: len(tmdb_id2matched_scripts[x]['scripts']) + random.randint(-5,5))
    num_docs = len(tmdb_id2matched_scripts.keys())
    ratios = {'train': 0.8, 'evaluation': 0.1, 'test': 0.1}

    set_sizes = {set_name: int(ratio * num_docs) for set_name, ratio in ratios.items()}

    sets = defaultdict(list)
    scripts_in_sets = defaultdict(list)

    # Sequentially add script into each set
    for tmdb_id in tmdb_ids:
        script_obj = tmdb_id2matched_scripts[tmdb_id]
        selected_set = min(set_sizes.keys(), key=lambda x: len(scripts_in_sets[x]))
        if tmdb_id not in tmdb_id2plot:
            continue
        sets[selected_set].append(tmdb_id)
        all_c = [c['tmdb_credit']['character'] for c in script_obj['scripts']]
        scripts_in_sets[selected_set] += [{
            'plot': tmdb_id2plot[tmdb_id],
            'character': c['tmdb_credit']['character'],
            'all_characters': all_c,
            'portion': c['portion'] * 100,
            'tmdb_id': tmdb_id,
            'character_id': c['tmdb_credit']['id'],
            'order': c['tmdb_credit']['order'],
        } for c in script_obj['scripts']]

        set_sizes[selected_set] -= 1
        if set_sizes[selected_set] == 0:
            del set_sizes[selected_set]


    for set_name, docs in sets.items():
        print(f"{set_name.title()} Set: {len(docs)}")
        print(f"\tCharacter count {len(scripts_in_sets[set_name])}")

    json.dump(scripts_in_sets, open('plot_portion_dataset.json','w'))