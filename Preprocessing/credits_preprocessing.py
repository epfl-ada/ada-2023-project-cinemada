import pandas as pd 
import json
import asyncio
import aiohttp
from tqdm import tqdm
import nest_asyncio
import os

nest_asyncio.apply()
api_key = os.environ['TMDB']
# Step 1: Download the list of person IDs
json_file_path = "dataset/person_ids.json"

# Read the JSON file line by line and append each line to a list
with open(json_file_path, 'r') as file:
    lines = file.readlines()

# Parse each line as a JSON object and store in a list
person_ids_data = [json.loads(line) for line in lines]

actors_ids = pd.DataFrame(person_ids_data)
print(actors_ids.shape[0])
actors_ids.head()
# Function to get actor information by person ID
async def get_actor_info(session, person_id):
    url = f'https://api.themoviedb.org/3/person/{person_id}?language=en-US'
    headers = {
        "Authorization": f"Bearer {api_key}",
        "accept": "application/json"
    }
    async with session.get(url, headers=headers) as response:
        if response.status == 200:
            return await response.json()
        else:
            print(f"Error for person ID {person_id}: {response.status}")
            return None
    
async def fetch_actor_info(session, person_id):
    actor_info = await get_actor_info(session, person_id)
    return actor_info

async def fetch_actor_info_batch(session, person_ids, results, lock):
    batch_results = []
    for person_id in person_ids:
        actor_info = await get_actor_info(session, person_id)
        batch_results.append(actor_info)

    async with lock:
        results.extend(batch_results)

async def main():
    num_requests = len(actors_ids["id"])

    async with aiohttp.ClientSession() as session:
        tasks = []
        results = []
        lock = asyncio.Lock()

        batch_size = 100  

        for i in range(0, num_requests, batch_size):
            person_ids_batch = actors_ids["id"][i:i+batch_size]
            task = fetch_actor_info_batch(session, person_ids_batch, results, lock)
            tasks.append(task)

        await asyncio.gather(*tasks)

    # Filter out None values and create a DataFrame
    results = [result for result in results if result is not None]
    actors_df = pd.DataFrame(results)

    # Save the DataFrame to a CSV file
    actors_df.to_csv('actors_info.csv', index=False)

    # Display the resulting dataframe
    actors_df.head()
    
def runcode():
    asyncio.run(main())
runcode()
# transform csv file into a dataframe
people_df = pd.read_csv('actors_info.csv')
actors_df = people_df[ 
    (people_df["name"].notna())
    ].copy()

actors_df.reset_index(drop=True, inplace=True)

columns_to_keep = ["id", "name", "popularity", "gender", 
                   "place_of_birth", "biography",
                   "also_known_as", "birthday", "deathday",
                   "imdb_id", "homepage", "profile_path"
                   ]
actors_df = actors_df[columns_to_keep]
actors_df.to_csv('output/actors_info.csv', index=False)

print(actors_df.size)
actors_df.head()

# get a list of 10 who have the highest popularity
actors_df.sort_values(by="popularity", ascending=False, inplace=True)
actors_df.reset_index(drop=True, inplace=True)
actors_df.head(10)