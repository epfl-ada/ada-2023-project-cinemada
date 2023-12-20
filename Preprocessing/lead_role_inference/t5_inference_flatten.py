from transformers import T5Tokenizer, T5ForConditionalGeneration
import json
import torch
from tqdm import tqdm
import re
import os

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
    results = json.load(open(save_data_path))     if os.path.exists(save_data_path) else {}
    device = 'mps' if torch.backends.mps.is_available() else 'cuda'
    valid_sets = []
    for tmdb_id in tmdb_ids:
        if str(tmdb_id) in gold_existed_tmdb_ids or tmdb_id in results:
            continue
        if str(tmdb_id) in tmdb_id2plot and str(tmdb_id) in tmdb_id2credit:
            for c in tmdb_id2credit[str(tmdb_id)]['cast']:
                valid_sets.append({
                    'tmdb_id': tmdb_id,
                    'plot': tmdb_id2plot[str(tmdb_id)],
                    'character_id': c['id'],
                    'character': c['character'],
                    'actor_name': c['name'],        
                })
    print(f'you requested : {len(tmdb_ids)}\n available: {len(valid_sets)}')
    tokenizer = T5Tokenizer.from_pretrained("t5-large")
    model = T5ForConditionalGeneration.from_pretrained("Hyeongdon/t5-large-character_plot_portion").to(device)
    results={}
    batch_size = 12
    batches = [valid_sets[i:i + batch_size] for i in range(0, len(valid_sets), batch_size)]

    model.eval()
    for batch_idx, batch in tqdm(enumerate(batches), total=len(batches)):
        prompts = [get_prompt(data['character'], data['plot']) for data in batch]
        model_inputs = tokenizer(prompts, max_length=2048, truncation=True, padding='max_length', return_tensors='pt')

        with torch.no_grad():
            probs = model.generate(input_ids=model_inputs['input_ids'].to(device), attention_mask=model_inputs['attention_mask'].to(device))

        for idx, prob in enumerate(probs):
            output_text = tokenizer.decode(prob, skip_special_tokens=True)
            output_dicts = batch[idx]
            output_dicts['output_text'] = output_text
            results[f"{output_dicts['tmdb_id']}__{output_dicts['character_id']}"] = output_dicts

        if batch_idx % 10 == 0 and batch_idx > 0:
            json.dump(results, open(save_data_path, 'w'))
