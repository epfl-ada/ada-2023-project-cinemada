from transformers import T5Tokenizer, T5ForConditionalGeneration
import json
import torch
from tqdm import tqdm
import re

tmdb_ids_path = '../tmdb_movie_ids.json'
tmdb_id2plot_path = './tmdb_id2plot_cmu_only.json'
tmdb_id2credit_path = './../../Data/tmdb_resources/tmdb_id2credit_full.json'
save_data_path = './portion_result.json'

def get_prompt(character_name, plot):
    c_name = re.sub(r'\([^)]*\)', '', character_name).strip()
    return f"Predict the percentage of a movie's plot that a character takes up.\nCharacter: {c_name} \nPlot: {plot}"

if __name__ == '__main__':
    tmdb_ids = json.load(open(tmdb_ids_path))
    tmdb_id2plot = json.load(open(tmdb_id2plot_path))
    tmdb_id2credit = json.load(open(tmdb_id2credit_path))
    gold_existed_tmdb_ids = json.load(open('gold_existed_tmdb_ids.json'))
    device = 'mps' if torch.backends.mps.is_available() else 'cuda'
    valid_sets = []
    for tmdb_id in tmdb_ids:
        if str(tmdb_id) in gold_existed_tmdb_ids:
            continue
        if str(tmdb_id) in tmdb_id2plot and str(tmdb_id) in tmdb_id2credit:
            valid_sets.append({
                'tmdb_id': tmdb_id,
                'plot': tmdb_id2plot[str(tmdb_id)],
                'characters': [
                    {
                        'id': c['id'],
                        'character': c['character'],
                        'name': c['name'],
                    } for c in tmdb_id2credit[str(tmdb_id)]['cast']
                ]
            })
    print(f'you requested : {len(tmdb_ids)}\n available: {len(valid_sets)}')
    tokenizer = T5Tokenizer.from_pretrained("t5-large")
    model = T5ForConditionalGeneration.from_pretrained("Hyeongdon/t5-large-character_plot_portion").to(device)
    results={}
    for data in tqdm(valid_sets):
        predictions = []
        for c in data['characters']:
            prompt = get_prompt(c['character'],data['plot'])
            model_inputs = tokenizer(prompt, max_length=2048, truncation=True, padding='max_length')
            model.eval()
            prob = model.generate(input_ids=torch.tensor([model_inputs['input_ids']]).to('mps'),attention_mask=torch.tensor([model_inputs['attention_mask']]).to('mps'))
            output_text = tokenizer.decode(prob[0], skip_special_tokens=True)
            try:
                output_portion = float(output_text)
            except:
                output_portion = 0
            predictions.append({
                'id': c['id'],
                'character': c['character'],
                'name': c['name'],
                'output_text': output_text,
                'output_portion': output_portion,
            })
        sum_portions = sum([p['output_portion'] for p in predictions])
        for p in predictions:
            p['scaled_portion'] = 100 * p['output_portion'] / sum_portions # note that it's a percentage.
        results[data['tmdb_id']] = predictions
        json.dump(results,open(save_data_path,'w'))