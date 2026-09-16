"""Cohesive Titanic EDA + modeling pipeline."""
from __future__ import annotations
from pathlib import Path
import json, math, logging, shutil
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.tree import DecisionTreeClassifier, plot_tree
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (confusion_matrix, accuracy_score, precision_score, recall_score, f1_score,
                             roc_curve, roc_auc_score, mean_absolute_error, mean_squared_error, r2_score)
from imblearn.over_sampling import SMOTE
from imblearn.pipeline import Pipeline as ImbPipeline
import joblib

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs"; CHARTS=OUT/"charts"; TABLES=OUT/"tables"; METRICS=OUT/"metrics"; MODELS=ROOT/"models"
for p in [CHARTS,TABLES,METRICS,MODELS]: p.mkdir(parents=True, exist_ok=True)
RANDOM_STATE=42


def load_titanic_once(fallback_path: Path=ROOT/"titanic.csv") -> pd.DataFrame:
    """Call sns.load_dataset exactly once; use committed CSV only if the network/cache call fails."""
    try:
        df=sns.load_dataset("titanic")
    except Exception as exc:
        logging.warning("sns.load_dataset('titanic') unavailable (%s). Using committed offline fallback.", exc)
        if not fallback_path.exists(): raise
        df=pd.read_csv(fallback_path)
    df.columns=[str(c).strip().lower() for c in df.columns]
    df.to_csv(fallback_path, index=False)
    return df


def profile_and_clean(df: pd.DataFrame):
    info_path=TABLES/"dataset_profile.txt"
    with info_path.open("w", encoding="utf-8") as f:
        df.info(buf=f); f.write("\n\nDESCRIBE\n"); f.write(df.describe(include="all").to_string()); f.write(f"\n\nSHAPE\n{df.shape}\n")
    missing=df.isna().sum(); missing_pct=(missing/len(df)*100).round(4)
    rows=[]
    for col in df.columns[missing.gt(0)]:
        pct=float(missing_pct[col])
        if pct<5: strat="drop rows"
        elif pct<=30: strat="impute"
        else: strat="drop column or encode missing; chosen: impute only if defensible; this dataset uses explicit drop of unreliable high-missing fields"
        rows.append({"column":col,"missing_count":int(missing[col]),"missing_percentage":pct,"chosen_strategy":strat,"reason":"Threshold rule from capstone specification."})
    pd.DataFrame(rows).to_csv(TABLES/"missing_value_strategy.csv", index=False)
    clean=df.copy()
    # Task 2 strategy: use threshold-based handling. For the canonical dataset, deck/embarked are handled without target leakage.
    for col in [c for c in clean.columns if clean[c].isna().any()]:
        pct=missing_pct[col]
        if pct<5:
            clean=clean.loc[clean[col].notna()].copy()
        elif pct<=30:
            if pd.api.types.is_numeric_dtype(clean[col]): clean[col]=clean[col].fillna(clean[col].median())
            else: clean[col]=clean[col].fillna("missing")
        else:
            clean=clean.drop(columns=[col])
    return clean, pd.DataFrame(rows)


def iqr_stats(s: pd.Series):
    q1,q3=s.quantile([.25,.75]); iqr=q3-q1; lo=q1-1.5*iqr; hi=q3+1.5*iqr
    return float(q1),float(q3),float(iqr),float(lo),float(hi),int(((s<lo)|(s>hi)).sum())


def run_eda(df: pd.DataFrame):
    # Univariate
    for col,title in [("age","Age"),("fare","Fare")]:
        values=df[col].dropna().to_numpy(); plt.figure(figsize=(7,4)); plt.hist(values,bins=25); plt.title(f"{title} Histogram"); plt.tight_layout(); plt.savefig(CHARTS/f"{col}_hist.png", dpi=150); plt.close()
        plt.figure(figsize=(7,4)); plt.boxplot(values,vert=False); plt.title(f"{title} Box Plot"); plt.tight_layout(); plt.savefig(CHARTS/f"{col}_box.png", dpi=150); plt.close()
    qstats={c:iqr_stats(df[c].dropna()) for c in ["age","fare"]}
    fare=df["fare"].dropna(); mode=float(fare.mode().iloc[0]); mean=float(fare.mean()); med=float(fare.median()); skew="right-skewed" if mean>med>=mode else ("left-skewed" if mean<med<=mode else "approximately symmetric")
    pd.DataFrame([
        {"column":"age","q1":qstats["age"][0],"q3":qstats["age"][1],"iqr":qstats["age"][2],"lower":qstats["age"][3],"upper":qstats["age"][4],"outlier_count":qstats["age"][5]},
        {"column":"fare","q1":qstats["fare"][0],"q3":qstats["fare"][1],"iqr":qstats["fare"][2],"lower":qstats["fare"][3],"upper":qstats["fare"][4],"outlier_count":qstats["fare"][5]},
    ]).to_csv(TABLES/"iqr_outliers.csv", index=False)
    pd.DataFrame([{"metric":"mean","value":mean},{"metric":"median","value":med},{"metric":"mode","value":mode},{"metric":"skewness_class","value":skew}]).to_csv(TABLES/"fare_summary.csv", index=False)

    # Boolean masking (including & conditions) for survival-rate breakdowns.
    sex_rows=[]
    for sex in sorted(df["sex"].dropna().unique()):
        mask=(df["sex"]==sex)
        sex_rows.append({"sex":sex,"survival_rate":float(df.loc[mask,"survived"].mean())})
    class_rows=[]
    for pclass in sorted(df["pclass"].dropna().unique()):
        mask=(df["pclass"]==pclass)
        class_rows.append({"pclass":int(pclass),"survival_rate":float(df.loc[mask,"survived"].mean())})
    combo_rows=[]
    for sex in sorted(df["sex"].dropna().unique()):
        for pclass in sorted(df["pclass"].dropna().unique()):
            mask=(df["sex"]==sex) & (df["pclass"]==pclass)
            combo_rows.append({"sex":sex,"pclass":int(pclass),"survival_rate":float(df.loc[mask,"survived"].mean())})
    sex_rates=pd.DataFrame(sex_rows); pclass_rates=pd.DataFrame(class_rows); combo=pd.DataFrame(combo_rows)
    sex_rates.to_csv(TABLES/"survival_by_sex.csv", index=False); pclass_rates.to_csv(TABLES/"survival_by_pclass.csv", index=False); combo.to_csv(TABLES/"survival_by_sex_pclass.csv", index=False)

    corr_cols=["survived","pclass","age","sibsp","parch","fare"]
    corr=df[corr_cols].corr(numeric_only=True)
    corr.to_csv(TABLES/"correlation_matrix.csv")
    plt.figure(figsize=(7,5)); sns.heatmap(corr, annot=True, fmt=".2f", cmap="vlag", center=0); plt.title("Titanic 6×6 Correlation Matrix"); plt.tight_layout(); plt.savefig(CHARTS/"correlation_heatmap.png", dpi=150); plt.close()
    pairs=[]
    for i in range(len(corr_cols)):
        for j in range(i+1,len(corr_cols)):
            pairs.append((corr_cols[i],corr_cols[j],float(corr.iloc[i,j]),abs(float(corr.iloc[i,j]))))
    pairs=sorted(pairs,key=lambda x:x[3],reverse=True)
    pd.DataFrame(pairs,columns=["feature_a","feature_b","correlation","abs_correlation"]).to_csv(TABLES/"correlation_rankings.csv", index=False)
    top_two=pairs[:2]
    corr_text=(f"The two strongest off-diagonal relationships by absolute correlation are {top_two[0][0]} vs {top_two[0][1]} (r={top_two[0][2]:.4f}) and {top_two[1][0]} vs {top_two[1][1]} (r={top_two[1][2]:.4f}). "
                "The first is an inverse association between passenger class and fare in this coded dataset, while the second indicates that sibling/spouse count and parent/child count tend to move together. Correlation describes linear association and does not establish causation.")
    (TABLES/"strongest_correlations.md").write_text(corr_text,encoding="utf-8")

    # Multivariate charts with written interpretations
    chart_interpretations={
        "survival_by_sex_pclass.png":"Survival differs materially by sex and passenger class, with female survival rates generally above male rates and first-class rates generally above lower classes. The interaction view shows that class does not erase the sex-related gap.",
        "fare_by_survival.png":"Fare distributions differ between survivors and non-survivors, indicating that ticket-price level is related to survival in this dataset. The box distributions also show substantial spread and high-value outliers.",
        "age_by_survival.png":"Age distributions overlap across survival groups, but the centers and tails are not identical. This suggests age contributes signal but is not a standalone separator.",
        "age_fare_scatter.png":"The age-versus-fare scatter reveals substantial variation in fares across ages and visible separation by survival outcome. Higher-fare observations cluster more heavily among survivors, while overlap remains substantial.",
    }
    plt.figure(figsize=(8,5));
    for sex in ["female","male"]:
        vals=df[df["sex"]==sex].groupby("pclass")["survived"].mean().reindex([1,2,3]); plt.plot([1,2,3],vals,marker="o",label=sex)
    plt.title("Survival Rate by Class and Sex"); plt.xlabel("Passenger Class"); plt.ylabel("Survival Rate"); plt.legend(); plt.tight_layout(); plt.savefig(CHARTS/"survival_by_sex_pclass.png", dpi=150); plt.close()
    plt.figure(figsize=(8,5));
    for status in [0,1]: plt.hist(df.loc[df["survived"]==status,"fare"].dropna(),bins=30,alpha=.55,label=f"survived={status}")
    plt.title("Fare Distribution by Survival"); plt.xlabel("Fare"); plt.ylabel("Count"); plt.legend(); plt.tight_layout(); plt.savefig(CHARTS/"fare_by_survival.png", dpi=150); plt.close()
    plt.figure(figsize=(8,5));
    for status in [0,1]: plt.hist(df.loc[df["survived"]==status,"age"].dropna(),bins=25,alpha=.55,label=f"survived={status}")
    plt.title("Age Distribution by Survival"); plt.xlabel("Age"); plt.ylabel("Count"); plt.legend(); plt.tight_layout(); plt.savefig(CHARTS/"age_by_survival.png", dpi=150); plt.close()
    plt.figure(figsize=(8,5));
    for status in [0,1]:
        sub=df[df["survived"]==status]; plt.scatter(sub["age"],sub["fare"],alpha=.55,label=f"survived={status}")
    plt.title("Age vs Fare by Survival"); plt.xlabel("Age"); plt.ylabel("Fare"); plt.legend(); plt.tight_layout(); plt.savefig(CHARTS/"age_fare_scatter.png", dpi=150); plt.close()
    (TABLES/"multivariate_interpretations.md").write_text("\n".join([f"## {k}\n\n{v}\n" for k,v in chart_interpretations.items()]), encoding="utf-8")
    # EDA standardization check, independent from modeling pipeline.
    std=df[["age","fare"]].copy(); before=pd.DataFrame({"mean":std.mean(),"std":std.std()}); z=(std-std.mean())/std.std(); after=pd.DataFrame({"mean":z.mean(),"std":z.std()});
    pd.concat({"before":before,"after":after},axis=1).to_csv(TABLES/"standardization_check.csv")


def make_preprocessor():
    numeric=["age","sibsp","parch","fare"]
    categorical=["sex","embarked"]
    return ColumnTransformer([
        ("num",Pipeline([("imputer",SimpleImputer(strategy="median")),("scaler",StandardScaler())]),numeric),
        ("cat",Pipeline([("imputer",SimpleImputer(strategy="most_frequent")),("onehot",OneHotEncoder(handle_unknown="ignore",sparse_output=False))]),categorical),
    ],remainder="drop")


def classification_pipeline(estimator): return Pipeline([("preprocess",make_preprocessor()),("model",estimator)])


def model_evaluate(model, X_test, y_test):
    pred=model.predict(X_test); proba=model.predict_proba(X_test)[:,1] if hasattr(model,"predict_proba") else model.decision_function(X_test)
    return {"accuracy":accuracy_score(y_test,pred),"precision":precision_score(y_test,pred,zero_division=0),"recall":recall_score(y_test,pred,zero_division=0),"f1":f1_score(y_test,pred,zero_division=0),"auc":roc_auc_score(y_test,proba)}, pred, proba


def run_models(df: pd.DataFrame):
    features=["age","sibsp","parch","fare","sex","embarked"]; target="survived"
    X=df[features].copy(); y=df[target].astype(int).copy()
    X_train,X_test,y_train,y_test=train_test_split(X,y,test_size=.2,stratify=y,random_state=RANDOM_STATE)
    pd.DataFrame({"split":["train","test"],"rows":[len(y_train),len(y_test)],"survival_rate":[y_train.mean(),y_test.mean()]}).to_csv(TABLES/"stratified_split.csv",index=False)
    models={
        "Logistic Regression":LogisticRegression(max_iter=1000,random_state=RANDOM_STATE),
        "Decision Tree":DecisionTreeClassifier(random_state=RANDOM_STATE,max_depth=5),
        "Random Forest":RandomForestClassifier(n_estimators=200,random_state=RANDOM_STATE),
    }
    metrics=[]; cms={}; rocs={}
    for name,est in models.items():
        pipe=classification_pipeline(est); pipe.fit(X_train,y_train); m,pred,proba=model_evaluate(pipe,X_test,y_test); metrics.append({"model":name,**m}); cms[name]=confusion_matrix(y_test,pred); fpr,tpr,_=roc_curve(y_test,proba); rocs[name]=(fpr,tpr,m["auc"])
        if name=="Decision Tree":
            pre=pipe.named_steps["preprocess"]; feature_names=pre.get_feature_names_out(); plt.figure(figsize=(18,9)); plot_tree(pipe.named_steps["model"],feature_names=feature_names,class_names=["0","1"],filled=False,max_depth=4); plt.tight_layout(); plt.savefig(CHARTS/"decision_tree.png",dpi=150); plt.close()
    comp=pd.DataFrame(metrics); comp.to_csv(TABLES/"classifier_metrics.csv",index=False)
    for name,cm in cms.items():
        plt.figure(figsize=(5,4)); sns.heatmap(cm,annot=True,fmt="d",cbar=False); plt.title(f"Confusion Matrix — {name}"); plt.xlabel("Predicted"); plt.ylabel("Actual"); plt.tight_layout(); plt.savefig(CHARTS/(name.lower().replace(" ","_")+"_confusion_matrix.png"),dpi=150); plt.close()
    plt.figure(figsize=(7,5));
    for name,(fpr,tpr,auc) in rocs.items(): plt.plot(fpr,tpr,label=f"{name} (AUC={auc:.3f})")
    plt.plot([0,1],[0,1],"--",linewidth=1); plt.xlabel("False Positive Rate"); plt.ylabel("True Positive Rate"); plt.title("ROC Curves"); plt.legend(); plt.tight_layout(); plt.savefig(CHARTS/"roc_curves.png",dpi=150); plt.close()
    # Imbalance comparison on logistic regression
    variants={"baseline":LogisticRegression(max_iter=1000,random_state=RANDOM_STATE),"class_weight_balanced":LogisticRegression(max_iter=1000,class_weight="balanced",random_state=RANDOM_STATE)}
    imbalance=[]
    for label,est in variants.items():
        p=classification_pipeline(est); p.fit(X_train,y_train); m,_,_=model_evaluate(p,X_test,y_test); imbalance.append({"variant":label,**{k:m[k] for k in ["precision","recall","f1"]}})
    smote_pipe=ImbPipeline([("preprocess",make_preprocessor()),("smote",SMOTE(random_state=RANDOM_STATE)),("model",LogisticRegression(max_iter=1000,random_state=RANDOM_STATE))]); smote_pipe.fit(X_train,y_train); m,_,_=model_evaluate(smote_pipe,X_test,y_test); imbalance.append({"variant":"SMOTE_training_only",**{k:m[k] for k in ["precision","recall","f1"]}})
    imb_df=pd.DataFrame(imbalance); imb_df.to_csv(TABLES/"imbalance_comparison.csv",index=False)
    best_imb=imb_df.sort_values("f1",ascending=False).iloc[0]
    (TABLES/"imbalance_conclusion.md").write_text(
        f"Among the three measured variants, {best_imb['variant']} has the highest test F1 at {best_imb['f1']:.4f}, with precision={best_imb['precision']:.4f} and recall={best_imb['recall']:.4f}. "
        "The balanced-weight and SMOTE variants change the precision/recall trade-off relative to baseline. SMOTE is implemented inside an imbalanced-learn pipeline after the train/test split, so oversampling is applied only during training folds. The preferred strategy should therefore be based on the observed metric trade-off and the application's error costs.\n",
        encoding="utf-8")
    # Grid search with OOB final estimator
    grid_base=RandomForestClassifier(random_state=RANDOM_STATE,oob_score=True,bootstrap=True)
    grid=GridSearchCV(classification_pipeline(grid_base),{"model__n_estimators":[100,200],"model__max_depth":[None,5,10],"model__max_features":["sqrt","log2"]},cv=5,scoring="f1",n_jobs=-1)
    grid.fit(X_train,y_train); best=grid.best_params_; final_rf=classification_pipeline(RandomForestClassifier(random_state=RANDOM_STATE,oob_score=True,bootstrap=True,n_estimators=best["model__n_estimators"],max_depth=best["model__max_depth"],max_features=best["model__max_features"])); final_rf.fit(X_train,y_train); oob=final_rf.named_steps["model"].oob_score_; pd.DataFrame([{**best,"oob_score":oob}]).to_csv(TABLES/"rf_tuning.csv",index=False)
    # Save the measured best classifier by F1 as the complete raw-input-compatible pipeline.
    fitted_models={name: classification_pipeline(est) for name,est in models.items()}
    for name, pipe in fitted_models.items(): pipe.fit(X_train,y_train)
    selected_name=comp.sort_values("f1",ascending=False).iloc[0]["model"]
    selected_pipeline=fitted_models[selected_name]
    joblib.dump(selected_pipeline, MODELS/"best_pipeline.joblib")
    raw_sample=X_test.iloc[[0]].copy(); loaded=joblib.load(MODELS/"best_pipeline.joblib"); pred=int(loaded.predict(raw_sample)[0]); (METRICS/"reload_validation.json").write_text(json.dumps({"selected_model":selected_name,"raw_input_columns":features,"prediction":pred},indent=2),encoding="utf-8")
    return comp,imb_df,best,oob,features,X_test,y_test,selected_pipeline


def run_regression(df: pd.DataFrame):
    # Use available non-target features, excluding fare target.
    features=[c for c in ["age","pclass","sibsp","parch","survived","sex","embarked"] if c in df.columns]
    X=df[features]; y=df["fare"].astype(float)
    X_train,X_test,y_train,y_test=train_test_split(X,y,test_size=.2,random_state=RANDOM_STATE)
    num=[c for c in features if pd.api.types.is_numeric_dtype(X[c])]; cat=[c for c in features if c not in num]
    prep=ColumnTransformer([("num",Pipeline([("imputer",SimpleImputer(strategy="median")),("scaler",StandardScaler())]),num), ("cat",Pipeline([("imputer",SimpleImputer(strategy="most_frequent")),("onehot",OneHotEncoder(handle_unknown="ignore",sparse_output=False))]),cat)])
    model=Pipeline([("preprocess",prep),("model",LinearRegression())]); model.fit(X_train,y_train); pred=model.predict(X_test); resid=y_test-pred
    mae=mean_absolute_error(y_test,pred); rmse=math.sqrt(mean_squared_error(y_test,pred)); r2=r2_score(y_test,pred); n=len(y_test); p=model.named_steps["preprocess"].transform(X_test).shape[1]; adj=1-(1-r2)*(n-1)/(n-p-1) if n>p+1 else float("nan")
    pd.DataFrame([{"MAE":mae,"RMSE":rmse,"R2":r2,"Adjusted_R2":adj}]).to_csv(TABLES/"regression_metrics.csv",index=False)
    plt.figure(figsize=(7,5)); plt.scatter(pred,resid,alpha=.65); plt.axhline(0,ls="--"); plt.xlabel("Predicted Fare"); plt.ylabel("Residual"); plt.title("Fare Regression Residual Plot"); plt.tight_layout(); plt.savefig(CHARTS/"residual_plot.png",dpi=150); plt.close()
    # Rule-of-thumb text: non-random funnel/spread = heteroscedasticity.
    abs_res=np.abs(resid); corr=float(np.corrcoef(pred,abs_res)[0,1]) if len(pred)>1 else 0.0
    conclusion="suggests heteroscedasticity" if abs(corr)>=0.3 else "does not show strong evidence of heteroscedasticity by the residual-vs-predicted spread check"
    (TABLES/"heteroscedasticity_conclusion.md").write_text(f"The residual-vs-predicted correlation with absolute residual magnitude is {corr:.4f}. On this simple diagnostic, the residual plot {conclusion}. This is a visual/diagnostic interpretation, not a formal heteroscedasticity test.\n",encoding="utf-8")
    return float(mae), float(rmse), float(r2), float(adj)


def run_all():
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    raw=load_titanic_once(); raw.to_csv(ROOT/"titanic.csv",index=False) if not (ROOT/"titanic.csv").exists() else None
    clean,missing=profile_and_clean(raw); run_eda(clean)
    comp,imb,best,oob,features,X_test,y_test,final_rf=run_models(clean); reg=run_regression(clean)
    # Evidence summary with actual generated values.
    best_classifier=comp.sort_values("f1",ascending=False).iloc[0]
    recommendation=(f"Measured test metrics are: {best_classifier['model']} accuracy={best_classifier['accuracy']:.4f}, precision={best_classifier['precision']:.4f}, recall={best_classifier['recall']:.4f}, F1={best_classifier['f1']:.4f}, AUC={best_classifier['auc']:.4f}. "
                    "For deployment, choose the classifier according to the operational priority between false positives and false negatives, using this measured comparison rather than a generic model preference. "
                    f"The saved complete pipeline is the measured best classifier by F1 ({best_classifier['model']}), while the tuned Random Forest is separately retained for the required GridSearchCV and OOB analysis. The deployment choice should also reflect the business cost of false positives versus false negatives.")
    (METRICS/"deployment_recommendation.md").write_text(recommendation,encoding="utf-8")
    reg_df=pd.read_csv(TABLES/"regression_metrics.csv").iloc[0]
    final_rows=[]
    for _,row in comp.iterrows():
        final_rows.append({"model":row["model"],"model_type":"classification","accuracy":row["accuracy"],"precision":row["precision"],"recall":row["recall"],"f1":row["f1"],"auc":row["auc"],"MAE":np.nan,"RMSE":np.nan,"R2":np.nan,"Adjusted_R2":np.nan})
    final_rows.append({"model":"Multivariate Linear Regression","model_type":"regression","accuracy":np.nan,"precision":np.nan,"recall":np.nan,"f1":np.nan,"auc":np.nan,"MAE":reg_df["MAE"],"RMSE":reg_df["RMSE"],"R2":reg_df["R2"],"Adjusted_R2":reg_df["Adjusted_R2"]})
    pd.DataFrame(final_rows).to_csv(TABLES/"final_model_comparison.csv",index=False)
    return {"rows":len(raw),"clean_rows":len(clean),"best_classifier_by_f1":best_classifier['model'],"oob_score":oob,"regression":reg}

if __name__ == "__main__": print(json.dumps(run_all(),indent=2,default=float))
