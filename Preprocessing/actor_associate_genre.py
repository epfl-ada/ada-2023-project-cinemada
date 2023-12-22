import json
import pandas as pd
import requests
import os
headers = {
    "accept": "application/json",
    "Authorization": os.environ['TMDB']
}

if __name__ == '__main__':
    json_data = json.load(open('../Data/tmdb_resources/tmdb_actors_db.json'))
    tmdb_actors = pd.json_normalize(json_data['results'], sep='_')

    # The column 'known_for' is a list of dictionaries. For each row, we wish to only keep the movies known for, not the media types == tv
    tmdb_actors['known_for'] = tmdb_actors['known_for'].apply(lambda x: [d for d in x if d['media_type'] == 'movie'])

    tmdb_actors
    tmdb_actors_name = pd.DataFrame(tmdb_actors['name'].unique(), columns=['name'])
    tmdb_actors['known_for'].loc[0]
    # Extracting 'genre_ids' from 'known_for' and adding it as a list to the DataFrame
    tmdb_actors_name['genre_ids'] = tmdb_actors['known_for'].apply(lambda x: [movie['genre_ids'] for movie in x] if x else [])
    #Extracting 'title' from known_for and adding it as a list to the DataFrame
    tmdb_actors_name['movies'] = tmdb_actors['known_for'].apply(lambda x: [movie['title'] for movie in x] if x else [])
    #Extracting popularity from known_for and adding it as a list to the DataFrame
    tmdb_actors_name['popularity'] = tmdb_actors['known_for'].apply(lambda x: [movie['popularity'] for movie in x] if x else [])
    display(tmdb_actors_name)
    # Get the list of possible movie genres



    url_movie = "https://api.themoviedb.org/3/genre/movie/list?language=en"
    response = requests.get(url_movie, headers=headers)
    genres = response.json()['genres']



    # Create a dictionary of genres with their ids as keys
    genre_dict = {}
    for genre in genres:
        genre_dict[genre['id']] = genre['name']
    # We first do a non-weighted count of the genres for each actor
    def genre_count(genre_ids):
        #transform a list of list into a list
        genre_ids = [item for sublist in genre_ids for item in sublist]
        if (len(genre_ids) == 0):
            return []

        genre_count = {}
        for genre_id in genre_ids:
            if genre_id in genre_count:
                genre_count[genre_id] += 1
            else:
                genre_count[genre_id] = 1

        # Now return the genre with the highest count
        genre_count = {k: v for k, v in sorted(genre_count.items(), key=lambda item: item[1], reverse=True)}

        # If there is a tie, return them all
        max_count = max(genre_count.values())
        genre_count = {k: v for k, v in genre_count.items() if v == max_count}
        if len(genre_count) > 1:
            return [genre_dict[genre_id] for genre_id in genre_count.keys()]
        else:
            return [genre_dict[list(genre_count.keys())[0]]]

    tmdb_actors_name['genre_mean'] = tmdb_actors_name['genre_ids'].apply(lambda x: genre_count(x))
    tmdb_actors_name

    def genre_weighted(genre_ids, popularity):
        #Multiply the genres by the popularity of their movie
        # Each sublist i gets multiplied by the popularity of the movie i
        genre_ids_mean = [[genre_id * popularity[i] for genre_id in sublist] for i, sublist in enumerate(genre_ids)]

        #transform a list of list into a list
        genre_ids_flatten = [item for sublist in genre_ids for item in sublist]
        if (len(genre_ids_flatten) == 0):
            return []

        genre_count = {}
        for list_id in range(len(genre_ids)):
            genre_movie = genre_ids[list_id]
            for id in range(len(genre_movie)):
                genre_id = genre_movie[id]
                weighted_genre_id = genre_ids_mean[list_id][id]
                if genre_id in genre_count:
                    genre_count[genre_id] += weighted_genre_id
                else:
                    genre_count[genre_id] = weighted_genre_id

        # Now return the genre with the highest count
        genre_count = {k: v for k, v in sorted(genre_count.items(), key=lambda item: item[1], reverse=True)}

        # If there is a tie, return them all
        max_count = max(genre_count.values())
        genre_count = {k: v for k, v in genre_count.items() if v == max_count}
        if len(genre_count) > 1:
            return [genre_dict[genre_id] for genre_id in genre_count.keys()]
        else:
            return [genre_dict[list(genre_count.keys())[0]]]


    tmdb_actors_name['genre_mean_weighted']  = tmdb_actors_name.apply(lambda x: genre_weighted(x['genre_ids'], x['popularity']), axis=1)
    display(tmdb_actors_name)
    # Display the genre_mean_weighted for Ryan Gosling
    tmdb_actors_name[tmdb_actors_name['name'] == 'Ryan Gosling']
    # Save the results to a csv file
    tmdb_actors_name.to_csv('../Data/preprocessed_data/actor_genre.csv', index=False)