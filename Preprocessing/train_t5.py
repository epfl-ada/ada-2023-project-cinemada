import json
scripts_in_sets = json.load(open('plot_portion_dataset.json'))
from datasets import Dataset
import pandas as pd
train_df = pd.DataFrame(scripts_in_sets['train'])
train_dataset = Dataset.from_pandas(train_df)
evaluation_df = pd.DataFrame(scripts_in_sets['evaluation'])
evaluation_dataset = Dataset.from_pandas(evaluation_df)

import re
def get_prompt(character_name, plot):
    c_name = re.sub(r'\([^)]*\)', '', character_name).strip()
    return f"Predict the percentage of a movie's plot that a character takes up.\nCharacter: {c_name} \nPlot: {plot}"


from transformers import T5Tokenizer, T5ForConditionalGeneration, Trainer, TrainingArguments


tokenizer = T5Tokenizer.from_pretrained('t5-large')

def preprocess_data(examples):
    inputs = [get_prompt(c_name,plot) for c_name,plot in zip(examples['character'],examples['plot'])]
    model_inputs = tokenizer(inputs, max_length=2048, truncation=True, padding='max_length')

    # Tokenize the targets with padding
    with tokenizer.as_target_tokenizer():
        labels = tokenizer([str(round(p,2)) for p in examples['portion']], max_length=128, truncation=True, padding='max_length')

    model_inputs['labels'] = labels['input_ids']
    return model_inputs

dataset = train_dataset
tokenized_train_dataset = train_dataset.map(preprocess_data, batched=True)
tokenized_validation_dataset = evaluation_dataset.map(preprocess_data, batched=True)
# tokenized_test_dataset = test_dataset.map(preprocess_data, batched=True)
model = T5ForConditionalGeneration.from_pretrained('t5-large').to('mps')
training_args = TrainingArguments(
    output_dir='./t5_large_results',
    num_train_epochs=1,
    per_device_train_batch_size=2,
    per_device_eval_batch_size=2,
    warmup_steps=500,
    weight_decay=0.01,
    logging_dir='./t5_large_logs',
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_train_dataset,
    eval_dataset=tokenized_validation_dataset,
)

trainer.train()
model.save_pretrained('./t5_large_trained_model')
