# Cinemada - Project Milestone 3
# Title: How do the roles of an actor influence their career?

## Data Story:
https://margg00.github.io

## Abstract:

In the world of cinema,  some actors often find themselves typecast, portraying specific personas across various movies, thereby becoming associated with particular genres and character archetypes. Some shine on the blockbuster’s screen and are known worldwide and acclaimed by the critics, meanwhile others are less popular and struggle to make a name for themselves in the industry. But how did they get there? Many actors tried to do the same but have not been as successful. How do the career trajectories differ between these two groups? This project aims to guide an actor wanna-be in his quest to success. To do so, we aim to analyze different actor’s trajectories depending on their success and understand its correlation with their first roles personas (romance, comedy, action,..) and role class (lead, secondary…). 

## Research Questions
In this project we aim to investigate the following questions:
- How do actor's first roles'types define their career path and trajectory?
- Is it a key to success to subsequently cast in more expensive movies?
- What is better for the actor's career: a lead role in a less-known/lower-budget movie or a secondary role in a successful/higher-budget movie?
- What is the importance of a lead role for the actor's career? Is it possible to make a successful career only with secondary roles?
- 
## Additional Datasets

- TMDB Database

  *Motivation* It contains information about the popularity and average ratings of actors and corresponding movies, which is necessary for analysis of an actor's success. Movie production budget and box office revenue data from this database are required for the high-budget role analysis.

  *Preprocessing* 
  It supports the IMDB key, wikidata key to search. For automatization, we also constructed a mapper for wikipedia_id -> tmdb_id.

- Databases with Oscar, Golden Globe and Critics Choice awards from Wiki
- YouGov database of the most popular Hollywood actors with their fame and popularity estimates
  
## Methods
**Initial analysis and preprocessing**

1. Classification of actors career trajectories (action stars, romantic leads, etc). We assign each actor the movie genres of their three most known movies / weighted average genre of their movies.

2. Identifying lead roles and secondary roles. To characterize role importance, we used movie scripts and extracted the portion of the script dedicated to a specific role. The higher the percentage, the more important the role. Since the scripts were available for only a portion of the movies in our dataset (around 10%), we used the plot summaries, which exist for every movie, to predict the portion dedicated to every character in the movie script. This was performed using Large Language Model. Using movie script data built from web crawling, we were able to get reliable labels for how much screen time individual characters get in each movie. Combining this with our movie plot data, we trained a Large Language model that takes a movie plot and a character name as input and outputs the percentage of the movie that character is in. The model we used is the T5-large model, which is suitable to deal with various tasks. Our trained model performs comparably to ChatGPT-3.5 on this task, and publicly available on https://huggingface.co/Hyeongdon/t5-large-character_plot_portion.

3. Success metric construction. Our metric of an actor's success can be based on two factors: 
 - awards (we consider 3 prestigiuos awards: Oscar, Golden Globe and Critics Choice) show an actor's recognition by the professional community
 - popularity shows an actor's recognition by the broad audience

 We use two sources of popularity estimation: a tmdB popularity of an actor and YouGov database of the most famous actors

We can aggregate these factors as follows:

$ Success(P, W) = P + F + \sqrt{W} $

In the formula P and F correspond to tmdB popularity and YouGov Fame, is the number of times the actor became an award winner or, in the case of Oscar, nominated. All terms are normalized, in the case of awards we're also taking the square root emphasizing the difference between 0 awards and at least 1 award.

**Main analysis**

We define the success of the actor by combining popularity and average people's votes data from the TMDB database. 
1. **Lead Role Analysis** We calculate various career success metrics for movies where the actor had a lead role and compare it to movies where they didn't. We visualize the impact of lead roles on an actor's career using bar charts or box plots. We aim to detect a correlation between the percentage of lead roles in an actor's career and their popularity and income.

2. **High-Budget Role Analysis** We compare career success metrics that do not rely on an actor's financial profit (e.g. popularity and people's votes) for actors, who appeared mostly in high-budget movies against low-budget ones. We can also check if the difference in mean success metric for high-budget vs low-budget actors is statistically significant by hypothesis testing.  We examine the influence of a movie genre and a prevalent role class (lead or secondary) to explore the following trade-off: better starring in a low-budget movie or taking a secondary role in a high-budget film.
   
3. **Genre Anlysis**: We compare the average genre of movies actors played in with their success metric and see if some correlation arises. We compute these values at different time-spans of the actor's career.

## Tasks:

* Lisa:
  - Data preprocessing for the regression analysis,
  - Genre analysis, construction
  - Preprocessing of success metric
* Doni:
  - External dataset preprocessing : By joining information from TMDB API and crawling method, obtained related external data from web source, and extracted mappers. Construct dataset for Train & Evaluate role portion estimation and train Large Language Model to extract role portion from plots.
* Marguerite:
   - Data Story
   - Pre-processing removing the actors that ended their careers a long time ago,
   - Time-scaling of popularity, analysis of the lead roles' influence on the succes.
* Sara:
   - Database extraction from TmDB and YouGOV
   - Actor's role analysis
   - Database preprocessing and division of actors into separate groups for analysis
   - Actor's career trajectory
* Yasmin:
  - SVR prediction of fame for complete dataset with explainability of the model,
  - Budget analysis
  - Worked with Marguerite on the lead role analysis
