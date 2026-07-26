import nbformat as nbf
import os

nb = nbf.v4.new_notebook()

text1 = """\
# EcoPackAI: Exploratory Data Analysis (EDA)
In this notebook, we explore the synthetic dataset generated for the packaging problem.
Our goal is to understand the distribution of dimensions, weight, fragility, and how they correlate with the chosen packaging types."""

code1 = """\
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')

# Set plotting style
plt.style.use('seaborn-v0_8-whitegrid')
sns.set_palette('muted')

# Load the dataset
df = pd.read_csv('../data/raw_packaging_data.csv')
df.head()"""

text2 = """\
## 1. Basic Dataset Information
Checking for missing values, data types, and basic statistics."""

code2 = """\
df.info()
display(df.describe())"""

text3 = """\
## 2. Target Variable Analysis (Packaging Type)
Let's see how our classes are distributed. As in real-world logistics, we expect high imbalance."""

code3 = """\
plt.figure(figsize=(10, 6))
sns.countplot(y='packaging_type', data=df, order=df['packaging_type'].value_counts().index)
plt.title('Distribution of Packaging Types', fontsize=14)
plt.xlabel('Count')
plt.ylabel('Packaging Type')
plt.tight_layout()
plt.show()"""

text4 = """\
## 3. Feature Distributions & Correlations
Let's analyze physical attributes (Length, Volume, Weight)."""

code4 = """\
# Calculate Volume for analysis
df['volume_cm3'] = df['length_cm'] * df['width_cm'] * df['height_cm']

fig, axes = plt.subplots(1, 2, figsize=(15, 5))
sns.histplot(df['weight_kg'], bins=50, ax=axes[0], kde=True)
axes[0].set_title('Distribution of Weight (kg)')

sns.histplot(df['volume_cm3'], bins=50, ax=axes[1], kde=True, color='orange')
axes[1].set_title('Distribution of Volume (cm³)')
plt.show()"""

text5 = """\
## 4. Bivariate Analysis
How do volume and weight influence the box size?"""

code5 = """\
plt.figure(figsize=(12, 8))
sns.scatterplot(x='volume_cm3', y='weight_kg', hue='packaging_type', data=df, alpha=0.6)
plt.title('Weight vs Volume colored by Packaging Type')
plt.show()"""

nb['cells'] = [
    nbf.v4.new_markdown_cell(text1),
    nbf.v4.new_code_cell(code1),
    nbf.v4.new_markdown_cell(text2),
    nbf.v4.new_code_cell(code2),
    nbf.v4.new_markdown_cell(text3),
    nbf.v4.new_code_cell(code3),
    nbf.v4.new_markdown_cell(text4),
    nbf.v4.new_code_cell(code4),
    nbf.v4.new_markdown_cell(text5),
    nbf.v4.new_code_cell(code5)
]

output_path = os.path.join(os.path.dirname(__file__), '01_exploratory_data_analysis.ipynb')
with open(output_path, 'w', encoding='utf-8') as f:
    nbf.write(nb, f)

print(f"Notebook created at {output_path}")
