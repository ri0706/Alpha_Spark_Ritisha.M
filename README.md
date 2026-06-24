import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder

# 1. Load data
df = pd.read_csv('doctors_combined_data.csv')

# 2. Clean structural anomalies
df = df.drop_duplicates()
df["Experience"] = pd.to_numeric(df["Experience"].replace("?", np.nan), errors="coerce")
df["Experience"] = df["Experience"].fillna(df["Experience"].median())

# 3. Categorical Binning & Encoding
bins = [0, 5, 10, 15, 20, 25, 30, 35, 40, 45, float('inf')]
labels = ['0-4', '5-9', '10-14', '15-19', '20-24', '25-29', '30-34', '35-39', '40-44', '45+']
df['Experience_Category'] = pd.cut(df['Experience'], bins=bins, labels=labels, right=False)

le = LabelEncoder()
df['Experience_Category_Encoded'] = le.fit_transform(df['Experience_Category'])

# 4. Generate high-dimensional sparse array
cat_cols = ['Education', 'Speciality', 'Chamber', 'Location', 'Concentration']
df_encoded = pd.get_dummies(df.drop(columns=['Doctor Name']), columns=cat_cols, drop_first=True)
