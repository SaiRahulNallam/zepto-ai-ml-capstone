# Analytics Pipeline

See the root README for setup and commands. The two notebooks are intentionally ordered: `01_eda.ipynb` creates/uses the single raw load and saves `titanic.csv`; `02_modeling.ipynb` reads the same CSV and continues through modeling. The modeling section uses a stratified split before a train-only `ColumnTransformer`/`Pipeline`, then evaluates Logistic Regression, Decision Tree, Random Forest, imbalance variants, a tuned OOB Random Forest, and a multivariate fare regression.

## Results

The validated pipeline produced:

- Dataset rows: 891
- Clean rows after preprocessing: 889
- Best classifier by F1: Decision Tree
- OOB score: 0.8073136427566807
- Regression MAE: 21.098604259640418
- Regression RMSE: 41.702104679032146
- Regression R²: 0.34816257216054314
- Regression Adjusted R²: 0.30913039085279115