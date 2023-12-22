import numpy as np
import json
import pandas as pd
from collections import defaultdict

def get_portion_by_order_logscale(order): # load as a backup method
    return np.power(np.e, 0.7756578 - 0.04791 * order)

def get_portion_by_order(order):
    return max(5.689275 -0.122673 * order, 0.001)

def get_order(tmdb_id, actor_id):
    credit = tmdb_id2credit[str(tmdb_id)]
    for j in credit['cast']:
        if str(j['id']) == str(actor_id):
            return j['order']
    raise ValueError('invalid actor')

def scaling(portions):
    total_portions = sum(list(portions.values())) + 0.0001
    return {k: 100*v / total_portions for k,v in portions.items()}

def hash_string(text):
    return text.lower().replace(' ','')
def name_match_and_get(tmdb_id,character_id,original_name,generated_dict):
    hashed_dict = {hash_string(k):v for k,v in generated_dict.items()}
    if hash_string(original_name) in hashed_dict:
        try:
            return float(str(hashed_dict[hash_string(original_name)]).replace('<','').replace('%','').strip())
        except:
            return get_portion_by_order_logscale(get_order(tmdb_id,character_id))
    return get_portion_by_order_logscale(get_order(tmdb_id,character_id))

if __name__ == '__main__':

    validation_set = json.load(open(root_path / 'Preprocessing/plot_portion_dataset.json'))['evaluation']
    validation_pred = {model_name: defaultdict(dict) for model_name in ['linear','log-linear','tmdb_order','T5-large','ChatGPT-3.5','ChatGPT-4']}
    tmdb_id2credit = json.load(open(root_path / 'Data/tmdb_resources/tmdb_id2credit_full.json'))
    target_tmdb_ids = set([v['tmdb_id'] for v in validation_set])

    for tmdb_id in target_tmdb_ids:
        credit = tmdb_id2credit[tmdb_id]
        portions_ll = {}
        portions_l = {}
        portions_o = {}
        for c in credit['cast']:
            portions_ll[str(c['id'])] = get_portion_by_order_logscale(c['order'])
            portions_l[str(c['id'])] = get_portion_by_order(c['order'])
            portions_o[str(c['id'])] = c['order']
        validation_pred['log-linear'][tmdb_id] = scaling(portions_ll)
        validation_pred['linear'][tmdb_id] = scaling(portions_l)
        validation_pred['tmdb_order'][tmdb_id] = scaling(portions_o)

    chatgpt_pred = json.load(open('chatgpt_pred.json'))
    chatgpt_pred_4 = json.load(open('chatgpt_4_pred.json'))

    for tmdb_id,v in chatgpt_pred.items():
        output_parsed = json.loads(v['gen_text'])
        parsed_prob = {}
        for character, c_id in v['character2id'].items():
            parsed_prob[c_id] = name_match_and_get(tmdb_id,str(c_id),character,output_parsed)
        prob_sum = sum(list(parsed_prob.values()))
        validation_pred['ChatGPT-3.5'][tmdb_id] = scaling(parsed_prob)

    for tmdb_id,v in chatgpt_pred_4.items():
        try:
            output_parsed = json.loads(v['gen_text'])
        except:
            output_parsed = {}
        parsed_prob = {}
        for character, c_id in v['character2id'].items():
            parsed_prob[c_id] = name_match_and_get(tmdb_id,c_id,character,output_parsed)
        validation_pred['ChatGPT-4'][tmdb_id] = scaling(parsed_prob)

    t5_output = json.load(open('lead_role_inference/t5_validation_inference.json'))
    for key, pred in t5_output.items():
        tmdb_id, actor_id = key.split('__')
        validation_pred['T5-large'][str(tmdb_id)][str(actor_id)]=float(pred['output_text'])
    for tmdb_id in target_tmdb_ids:
        credit = tmdb_id2credit[tmdb_id]
        for c in credit['cast']:
            if str(c['id']) not in validation_pred['T5-large'][tmdb_id]:
                validation_pred['T5-large'][tmdb_id][str(c['id'])] = get_portion_by_order_logscale(c['order'])
        validation_pred['T5-large'][tmdb_id] = scaling(validation_pred['T5-large'][tmdb_id])

    json.dump(validation_pred,open('validation_pred.json','w'))