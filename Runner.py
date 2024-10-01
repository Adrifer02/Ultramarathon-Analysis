# Welcome to my project about Ultramarathon runners
# Import libraries
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import scipy.stats as stats

# Import Dataframe
df= pd.read_csv("C:\\Users\\ADRIAN\\Desktop\\Portfolio\\DataAnalyst\\Runner\\archive\\TWO_CENTURIES_OF_UM_RACES.csv")

# Clean up Data
# Step 1 - Only 50km, 50mi and races from USA in 2020
df1 = df[(df['Event distance/length'].isin(['50km', '50mi'])) & (df['Year of event']==2020) & (df['Event name'].str.split('(').str.get(1).str.split(')').str.get(0)=='USA')]

# Step 2 - Remove USA from Events Name
df1['Event name']= df1['Event name'].str.split('(').str.get(0)

# Step 3 - Cleaning up athlete age
df1['athlete_age'] = 2020 - df1['Athlete year of birth']

# Step 4 - Remove 'h' from athlete performance
df1['Athlete performance']= df1['Athlete performance'].str.split(' ').str.get(0)

# Step 5 - Drop columns: Athlete club, Athlete Country, Athlete year of birth, Athlete age category
df1 = df1.drop(['Athlete club', 'Athlete country', 'Athlete year of birth', 'Athlete age category'], axis=1)

# Step 6 - Clean up null values
df1 = df1.dropna()

# Step 7 - Check for duplicates
df1[df1.duplicated() == True]

# Step 8 - Reset index
df1.reset_index(drop=True)

# Step 9 - Fix types
df1['athlete_age'] = df1['athlete_age'].astype(int)
df1['Athlete average speed'] = df1['Athlete average speed'].astype(float)

# Step 10 - Rename columns
df1 = df1.rename(columns={'Year of event': 'year',
                          'Event dates': 'race_day',
                          'Event name': 'race_name',
                          'Event distance/length': 'race_length',
                          'Event number of finishers': 'race_number_of_finishers',
                          'Athlete performance': 'athlete_performance',
                          'Athlete gender': 'athlete_gender',
                          'Athlete average speed': 'athlete_average_speed',
                          'Athlete ID': 'athlete_id'})

# Step 11 - Reorder columns
df2 = df1[['race_day', 'race_name', 'race_length', 'race_number_of_finishers', 'athlete_id', 'athlete_gender', 'athlete_average_speed', 'athlete_performance', 'athlete_age']]

# Step 12 - Create charts and graphs
# 1. The gender distribution of the runners with respect to the race distance
sns.histplot(df2, x='race_length', hue='athlete_gender')
#plt.show()

# 2. Average speed of athletes in 50-mile races
sns.displot(df2[df2['race_length']=='50mi']['athlete_average_speed'])
#plt.show()

# 3. Distribution of Athletes' Average Speed by Race Distance and Gender
sns.violinplot(data=df2, x='race_length', y='athlete_average_speed', hue='athlete_gender', split=True, inner='quart', linewidth=1)
#plt.show()

# 4. Relationship between athlete age and average speed
sns.lmplot(data=df2, x='athlete_age', y='athlete_average_speed', hue='athlete_gender')
#plt.show()

# Question I want to find out with the data
# 1. Difference in speed for the 50km, 50mi male to female
speed_diff = df2.groupby(['race_length', 'athlete_gender'])['athlete_average_speed'].mean()
print("Average speed difference between male and female for 50km and 50mi:")
print(speed_diff)

# 2. What age groups are the best in the 50mi race (20+ races min)
age_group_best_performance = df2.query('race_length == "50mi"').groupby('athlete_age')['athlete_average_speed'].agg(['mean', 'count']).sort_values('mean', ascending=False).query('count > 19').head(15)
print("Top performing age groups in 50mi race (with at least 20 races):")
print(age_group_best_performance)

# 3. What age groups are the worst in the 50mi race (10+ races min)
age_group_worst_performance = df2.query('race_length == "50mi"').groupby('athlete_age')['athlete_average_speed'].agg(['mean', 'count']).sort_values('mean', ascending=True).query('count > 9').head(20)
print("Worst performing age groups in 50mi race (with at least 10 races):")
print(age_group_worst_performance)

# Question 1: Differences in speed between male and female in 50km and 50mi races
for race in ['50km', '50mi']:
    male_speed = df2[(df2['race_length'] == race) & (df2['athlete_gender'] == 'M')]['athlete_average_speed']
    female_speed = df2[(df2['race_length'] == race) & (df2['athlete_gender'] == 'F')]['athlete_average_speed']
    t_stat, p_value = stats.ttest_ind(male_speed, female_speed)
    print(f"T-test for {race} between male and female: T-stat = {t_stat:.2f}, p-value = {p_value:.5f}")

# Question 2: Create a season column to analyze performance by season
df2['race_month'] = df2['race_day'].str.split('.').str.get(1).astype(int)
df2['race_season'] = df2['race_month'].apply(lambda x: 'Winter' if x > 11 else 'Fall' if x > 8 else 'Summer' if x > 5 else 'Spring' if x > 2 else 'Winter')
print(df2.head(25))

# Group by season and only 50km
group_by_season = df2.query('race_length == "50km"').groupby('race_season')['athlete_average_speed'].agg(['mean', 'count']).sort_values('mean', ascending=False)
print(group_by_season)

# Question 3: Bar plot for average speed by season
sns.barplot(data=group_by_season.reset_index(), x='race_season', y='mean')
plt.title("Average speed of athletes by season (50km)")
plt.show()

# Question 4: Correlation between age and average speed
for race in ['50km', '50mi']:
    subset = df2[df2['race_length'] == race]
    correlation, p_value = stats.pearsonr(subset['athlete_age'], subset['athlete_average_speed'])
    print(f"Correlation between age and average speed in {race}: Correlation = {correlation:.2f}, p-value = {p_value:.5f}")