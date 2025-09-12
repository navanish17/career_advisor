import pandas as pd
df = pd.read_csv('C:\Project\career_advisor\quiz_q.csv')
df = df.T #transposing our data
print(df.head())

mapping = {}

for i in range(1,11):
    mapping[f"Q{i}"] = 'Science'

for i in range(10,21):
    mapping[f"Q{i}"] = 'Commerce'

