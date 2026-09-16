# Analytics Pipeline

See the root README for setup and commands. The two notebooks are intentionally ordered: `01_eda.ipynb` creates/uses the single raw load and saves `titanic.csv`; `02_modeling.ipynb` reads the same CSV and continues through modeling. The modeling section uses a stratified split before a train-only `ColumnTransformer`/`Pipeline`, then evaluates Logistic Regression, Decision Tree, Random Forest, imbalance variants, a tuned OOB Random Forest, and a multivariate fare regression.
