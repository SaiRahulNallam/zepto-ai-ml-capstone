import json
from pathlib import Path
import pandas as pd
import json
from analytics.src.pipeline import profile_and_clean, iqr_stats, make_preprocessor, classification_pipeline, run_models
from sklearn.linear_model import LogisticRegression

FIX=Path(__file__).resolve().parents[1]/"titanic.csv"

def test_offline_csv_exists(): assert FIX.exists(); df=pd.read_csv(FIX); assert not df.empty

def test_profile_clean_and_outliers():
    df=pd.read_csv(FIX); clean,missing=profile_and_clean(df)
    assert "missing_percentage" in missing.columns if not missing.empty else True
    assert len(iqr_stats(clean["age"].dropna()))==6

def test_pipeline_fit_and_raw_prediction():
    df=pd.read_csv(FIX); clean, _=profile_and_clean(df)
    pipe=classification_pipeline(LogisticRegression(max_iter=500)); X=clean[["age","sibsp","parch","fare","sex","embarked"]]; y=clean["survived"]; pipe.fit(X,y); pred=pipe.predict(X.iloc[[0]]); assert pred.shape==(1,)


def test_saved_pipeline_artifact_and_reload_validation():
    artifact=Path(__file__).resolve().parents[1]/"models"/"best_pipeline.joblib"
    evidence=Path(__file__).resolve().parents[1]/"outputs"/"metrics"/"reload_validation.json"
    assert artifact.exists()
    assert evidence.exists()
    payload=json.loads(evidence.read_text())
    assert payload["selected_model"] in {"Logistic Regression","Decision Tree","Random Forest"}
