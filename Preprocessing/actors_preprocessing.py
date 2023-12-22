import requests
import json
import pandas as pd
import os
api_key = os.environ['TMDB']
# Used to fetch data from TMDB API and save to a JSON file. Needed to be run only once.

url = 'https://api.themoviedb.org/3/person/popular'
headers = {
    "Authorization": f"Bearer {api_key}",
    "accept": "application/json"
}

def fetch_page(page):
    params = {'language': 'en-US', 'page': page}
    response = requests.get(url, params=params, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        print(f"Page {page} processed.")
        return data['results']
    else:
        print(f"Error: {response.status_code}, {response.text}")
        return []
    
def fetch_all_pages():
    all_data = []
    for page in range(1, 500):
        page_results = fetch_page(page)
        all_data.extend(page_results)

    return all_data

def fetch_process():
    all_data = fetch_all_pages()

    # Save all data to a single file
    with open('../Data/tmdb_resources/tmdb_actors_db.json', 'w') as f:
        json.dump({'results': all_data}, f)

    print("Data fetching and appending complete.")

def get_popular_movies(actor_name):
    actor_movies = actors_df[actors_df['name'] == actor_name]['known_for'].values[0]
    popular_movies = sorted(actor_movies, key=lambda x: x['popularity'], reverse=True)
    return popular_movies
    
if __name__ == '__main__':
    fetch_process()
    json_file_path = "../Data/tmdb_resources/tmdb_actors_db.json"

    # Read JSON data from the file
    with open(json_file_path, 'r') as file:
        json_data = json.load(file)

    # Convert to DataFrame
    actors_df = pd.json_normalize(json_data['results'], sep='_')

    # Extracting 'original_language' from 'known_for' and adding it to the DataFrame
    actors_df['original_language'] = actors_df['known_for'].apply(lambda x: x[0]['original_language'] if x else None)
    # Extracting 'genre_ids' from 'known_for' and adding it as a list to the DataFrame
    actors_df['genre_ids'] = actors_df['known_for'].apply(lambda x: [genre['genre_ids'] for genre in x] if x else [])

    actors_df = actors_df[actors_df['known_for_department'] == "Acting"]
    ordered_columns = ["name", "gender", "popularity", "original_language", "genre_ids" , "known_for", "id"]
    actors_df = actors_df[ordered_columns]
    actors_df.to_csv('../Data/preprocessed_data/actors_db.csv', index=False)

    print(f"There are {actors_df.shape[0]} actors in the dataset.")
    display(actors_df)

    #Example:  Get information about the 3 most popular movies of the actor Jackie Chan


    example_df = pd.json_normalize(get_popular_movies("Jackie Chan"))
    ordered_columns = ["title", "popularity", "original_language", "genre_ids", "release_date", "vote_average", "vote_count", "id", "overview"]
    example_df[ordered_columns]