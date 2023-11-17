# Cinemada - Project Milestone 2
# Title: How do the roles of an actor influence their career?

## Abstract:

In the world of cinema,  some actors often find themselves typecast, portraying specific personas across various movies, thereby becoming associated with particular genres and character archetypes. Some shine on the blockbuster’s screen and are known worldwide and acclaimed by the critics, meanwhile others are less popular and struggle to make a name for themselves in the industry. But how did they get there? Many actors tried to do the same but have not been as successful. How do the career trajectories differ between these two groups? This project aims to guide an actor wanna-be in his quest to success. To do so, we aim to analyze different actor’s trajectories depending on their success and understand its correlation with their first roles personas (romance, comedy, action,..) and role class (lead, secondary…). 

## Research Questions
In this project we aim to investigate the following questions:
- How do actor's first roles'types define their career path and trajectory?
- Is it a key to success to subsequently cast in more expensive movies?
- What is better for the actor's career: a lead role in a less-known/lower-budget movie or a secondary role in a successful/higher-budget movie?
- What is the importance of a lead role for the actor's career? Is it possible to make a successful career only with secondary roles?
  
## Additional Datasets

- TMDB Database

  **Motivation** It contains information about the popularity and average ratings of actors and corresponding movies, which is necessary for analysis of an actor's success. Movie production budget and box office revenue data from this database are required for the high-budget role analysis.

  **Preprocessing** 
  It supports the IMDB key, wikidata key to search. For automatization, we also constructed a mapper for wikipedia_id -> tmdb_id.


## Methods
**Initial analysis and preprocessing**

1. Classification of actors career trajectories (action stars, romantic leads, etc). We assign each actor the movie genres of their three most known movies / weighted average genre of their movies based on the success of movies.

2. Identifying lead roles and secondary roles  based on the number of occurrences of the characters' names in the synopsis.

3. Classification of the high-budget/low-budget roles based on production budgets and revenues of the movies. We find a suitable criterion to categorize films into low-budget and high-budget groups, which mantains similar proportions of the movies with high success rate in each group.

**Main analysis**

We defining the success of the actor combining popularity and average people's votes data from the TMDB database. 
1. **Lead Role Analysis** We calculate various career success metrics for movies where the actor had a lead role and compare it to movies where they didn't. We visualize the impact of lead roles on an actor's career using bar charts or box plots. We aim to decect correlation between the percentage of lead roles in an actor's career and their popularity and income.

2. **High-Budget Role Analysis** We compare career success metrics that do not rely on an actor's financial profit (e.g. popularity and people's votes) for actors, who appeared mostly in high-budget movies against low-budget ones. We can also check if the difference in mean success metric for high-budget vs low-budget actors is statistically significant by hypothesis testing.  We examine the influence of a movie genre and a prevalent role class (lead or secondary) to explore the following trade-off: better starring in a low-budget movie or taking a secondary role in a high-budget film.
   
3. **Career Defining Analysis** We explore if debut roles influence the subsequent roles of an actor and their career trajectory class. For it we plot the histograms to display the distribution of career trajectories classes based on the persona of the first role. The latter information will be extracted from the CMU dataset's character clusters.

4. **Career Trajectory Analysis** We expand the previous analysis by tracking an actor's career progression. We identify key milestones in their career, such as the first lead role, different class of role taken or breakthrough performance and make chronological plot with rating/success.

## Proposed timeline and internal milestones

**Oct 29 - Nov 17**: Data exploration and preprocessing, formulation of the research questions and hypotheses

**Nov 18 - Nov 28**: Construction of all the charts and plots needed for each analysis (Dividing the work on parts 1-4 of the main analysis across the 5 group members)

**Nov 29 - Dec 8**: Results analysis and correlation investigation

**Dec 9 - Dec 12**: Discussion and review of results between teams and cross-comparison

**Dec 13 - Dec 22**: Final validation of the results, design of a data story
