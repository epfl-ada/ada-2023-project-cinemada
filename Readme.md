# Cinemada - Project 2
## Title: How do the roles of an actor influence their career?
## Abstract:
## Research Questions:
- Does an actor's debut role define their career and the types of roles they will play?
- Is it a key to success to subsequently cast in more expensive movies?
- What is better for the actor's career: a lead role in a less-known/lower-budget movie or a secondary role in a successful/higher-budget movie?
- What is the importance of a lead role for the actor's career? Is it possible to make a successful career only with a secondary roles?
## Additional Datasets:
- TMDB Database

  **Motivation** It contains information about the popularity and average ratings of actors and corresponding movies, which is necessary for analysis of an actor's success. Movie production budget and box office revenue data from this database are required for the high-budget role analysis.

  **Preprocessing** 
  It supports the IMDB key, wikidata key to search. For automatization, we also constructed a mapper for wikipedia_id -> tmdb_id.


## Methods:
**Initial analysis and preprocessing**

1. Classification of actors career trajectories (action stars, romantic leads, etc). We assign each actor the movie genres of their three most known movies / weighted average genre of their movies based on the success of movies.

2. Identifying lead roles and secondary roles  based on the number of occurrences of the characters' names in the synopsis

3. Classification of the high-budget/low-budget roles based on production budgets and revenues of the movies 

4. Defining the success of the actor combining popularity and average ratings data from the TMDB database

**Main analysis**

1. **Lead Role Analysis** We calculate various career success metrics (e.g., popularity, people's votes, awards (??? we don't have data for it), box office earnings) for movies where the actor had a lead role and compare it to movies where they didn't. We visualize the impact of lead roles on an actor's career using bar charts or box plots.

2. **High-Budget Role Analysis** TBD
3. **Career Defining Analysis** We explore if debut roles influence the subsequent roles of an actor and their career trajectory. For it we plot the histograms to display the distribution of career trajectories based on the first role.

4. **Career Trajectory Analysis** We expand the previous analysis by tracking an actor's career progression. We identify key milestones in their career, such as the first lead role, different class of role taken or breakthrough performance and make chronological plot with rating/success.

## Timeline:

![Gantt Chart](Support\timeline.png)


**Oct 29 - Nov 17**: Data preprocessing and formulation of the research questions and hypotheses

**Nov 18 - Nov 24**: Lead Role Analysis

**Nov 25 - Dec 1**: High-Budget Role Analysis

**Dec 2 - Dec 8**: Career Defining Analysis

**Dec 9 - Dec 15**: Career Trajectory Analysis

**Dec 16 - Dec 22**: Final validation of the results and creating a presentation of the whole datastory



## Milestones:

## Questions for TA:
