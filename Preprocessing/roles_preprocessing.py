import nltk
import pandas as pd
from nltk import ne_chunk, pos_tag, word_tokenize
from nltk.tree import Tree

if __name__ == '__main__':

    nltk.download('punkt')
    nltk.download('averaged_perceptron_tagger')
    nltk.download('maxent_ne_chunker')
    nltk.download('words')
    pd.set_option('display.max_colwidth', None)
    data_folder = './Data/MovieSummaries/'
    movies = pd.read_csv(data_folder+'movie.metadata.tsv', sep='\t', header=None,  names = ['Wiki ID','movie ID','name', 'release date', 'BOR', 'runtime','languages','countries','genres'])
    char= pd.read_csv(data_folder+'character.metadata.tsv', sep='\t', header=None,  names = ['Wiki ID','movie ID', 'release date', 'char name','DOB', 'gender','heght','ethnicity','actor name', 'actor age', 'map ID', 'char ID', 'actor ID' ])

    names_char = pd.read_csv(data_folder+'name.clusters.txt', sep='\t', header=None, names=['Name', 'char ID'] )
    summaries_path = data_folder+'plot_summaries.txt' 
    movie_summaries = pd.DataFrame(columns=['Wiki ID', 'Summary'])

    with open(summaries_path, 'r', encoding='utf-8') as file:
        for line in file:
            parts = line.strip().split('\t')
            row=pd.DataFrame([{'Wiki ID': int(parts[0]), 'Summary': parts[1]}])
            movie_summaries = pd.concat([movie_summaries,row],axis=0, ignore_index=True)
    movie_summaries=movie_summaries.dropna()
    char=char.dropna(subset=['Wiki ID', 'char name'])
    char['role']=int(0)
    print("Number of movies:", movies.shape[0])
    print("Number of summaries:", movie_summaries.shape[0])
    n_movie_in_char = char.drop_duplicates(subset='Wiki ID', keep='first')
    print("Number of movies where we know the characters:", n_movie_in_char.shape[0])
    common_index = movies['Wiki ID'].isin(movie_summaries['Wiki ID']) & movies['Wiki ID'].isin(char['Wiki ID'])
    filtered_movies = movies[common_index]
    name=''
    for i in filtered_movies.index:
        plot=str(movie_summaries[movie_summaries['Wiki ID']==filtered_movies.loc[i]['Wiki ID']]['Summary'])
        char_names=char[char['Wiki ID']==filtered_movies.loc[i]['Wiki ID']]['char name']

        # Split the summary in words
        n_words=len(plot.split())
        names=[]
        name_groups = {}

        # Detect names in summary
        if n_words>=2:
            print("Summary of film {0}:".format(i), plot)
            # Perform Name Entity Recognition using NLTK 
            nltk_results = ne_chunk(pos_tag(word_tokenize(plot)))
            for nltk_result in nltk_results:
                if type(nltk_result) == Tree:
                    name = ''
                    # Extract words from result and add to name list
                    for nltk_result_leaf in nltk_result.leaves():
                        name += nltk_result_leaf[0] + ' '
                    names.append(name)



        # Divide name in last and first name, disgard longer names
        for name in names:
            match_found = False
            name_parts = name.strip().lower().split()
            if len(name_parts) == 2:
                #If full name
                first_name, last_name = name_parts
            elif len(name_parts) == 1:
                #If single name
                first_name, last_name= name_parts[0],""
            else:
                break
            full_name = (first_name, last_name)


            # If name mentionned multiple times, group the mentions
            for group, members in name_groups.items():
                if len(name_parts) == 1:
                    if first_name in group[0] or first_name in group[1]:
                        members.append(name)
                        match_found = True
                elif first_name in group[0] or last_name in group[1] or first_name in group[1] or last_name in group[0]:
                    members.append(name)
                    match_found = True
                    break

            if not match_found:
                name_groups[full_name] = [name]


        # Match names detected to character of char dataset
        for name in char_names:
            mention=False
            char_name_parts = name.strip().lower().split()
            for group, members in name_groups.items():
                for word in char_name_parts:
                    if word in group:
                        #print("Name", name, "has", len(members), "mentions")
                        char.loc[char['char name'] == name, 'role'] = int(len(members))
                        mention=True
                        break
            if mention==False:
                char.loc[char['char name'] == name, 'role'] = 0
                #print("Name", name, "has", 0, "mentions")

    char.to_csv('Data\proprocessed_data\char_with_roles.csv', index=False)
    char= pd.read_csv('Data\proprocessed_data\char_with_roles.csv')
    char_filtered=char
    for i, movie_id in enumerate(char['Wiki ID'].unique()):
        characters=char_filtered[char_filtered['Wiki ID'] == movie_id]
        if all(characters['role'] == 0):
            char_filtered=char_filtered.drop(characters.index)
    char_filtered.to_csv('Data\proprocessed_data\char_with_roles_filtered.csv', index=False)