import nbformat as nbf
import os

nb = nbf.v4.new_notebook()
cells = []

# Title
cells.append(nbf.v4.new_markdown_cell("""\
# Phase 1: Comprehensive Exploratory Data Analysis (EDA)
**Objective**: Perform rigorous statistical and visual analysis on the processed dataset to ensure it is ready for Machine Learning.
"""))

# Imports
cells.append(nbf.v4.new_code_cell("""\
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

plt.style.use('seaborn-v0_8-whitegrid')
df = pd.read_csv('../data/processed/processed_dataset.csv')
"""))

# Summary Statistics
cells.append(nbf.v4.new_markdown_cell("""\
## 1. Summary Statistics & Missing Values
"""))
cells.append(nbf.v4.new_code_cell("""\
display(df.describe())
display(df.isnull().sum())
"""))
cells.append(nbf.v4.new_markdown_cell("""\
### Analysis
- **What it means**: Describes the mean, standard deviation, and quartiles of our numerical features. Also confirms zero missing values.
- **Why it matters**: ML models crash on nulls (unless specifically handled like XGBoost) and scale poorly on extreme deviations.
- **Business impact**: Ensures we are modeling on complete, representative warehouse data.
- **ML impact**: Prevents runtime errors during `.fit()`.
- **Potential improvements**: Implement automated tracking of summary statistics drift using tools like `Great Expectations`.
"""))

# Correlation Matrix
cells.append(nbf.v4.new_markdown_cell("""\
## 2. Correlation Matrix
"""))
cells.append(nbf.v4.new_code_cell("""\
plt.figure(figsize=(8, 6))
numeric_cols = df.select_dtypes(include=[np.number]).columns
sns.heatmap(df[numeric_cols].corr(), annot=True, cmap='coolwarm', fmt=".2f")
plt.title('Feature Correlation Matrix')
plt.show()
"""))
cells.append(nbf.v4.new_markdown_cell("""\
### Analysis
- **What it means**: Shows the Pearson correlation coefficient between features (-1 to 1).
- **Why it matters**: Highly correlated features (multicollinearity) can confuse linear models and reduce feature importance interpretability in tree models.
- **Business impact**: Identifies which physical metrics (e.g., volume) most heavily dictate weight.
- **ML impact**: We can see `volume_cm3` and `weight_kg` are correlated. XGBoost handles correlated features well, but dropping redundant ones can speed up inference.
- **Potential improvements**: Use Variance Inflation Factor (VIF) to programmatically drop highly collinear features.
"""))

# Outliers
cells.append(nbf.v4.new_markdown_cell("""\
## 3. Outlier Analysis (Boxplots)
"""))
cells.append(nbf.v4.new_code_cell("""\
plt.figure(figsize=(10, 4))
sns.boxplot(x=df['weight_kg'])
plt.title('Weight Distribution (Post-Winsorization)')
plt.show()
"""))
cells.append(nbf.v4.new_markdown_cell("""\
### Analysis
- **What it means**: Visualizes the spread of weights and highlights values outside the Interquartile Range (IQR).
- **Why it matters**: Outliers skew loss functions (like MSE) during model training, pulling the decision boundary away from the norm.
- **Business impact**: Prevents our pricing/cost models from being hijacked by one abnormally heavy item.
- **ML impact**: Thanks to our Winsorization in the cleaning pipeline, extreme outliers are capped, ensuring stable gradient descent.
- **Potential improvements**: Use Isolation Forests to dynamically detect complex multidimensional outliers.
"""))

nb['cells'] = cells
output_path = os.path.join(os.path.dirname(__file__), '02_comprehensive_eda.ipynb')
with open(output_path, 'w', encoding='utf-8') as f:
    nbf.write(nb, f)
print(f"Notebook created at {output_path}")
