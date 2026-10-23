# trains models to predict pace_delta_s and tests them on races they haven't seen

import pandas as pd
import numpy as np
from sklearn.dummy import DummyRegressor
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import LeaveOneGroupOut
from sklearn.metrics import mean_absolute_error

print("Loading dataset...")
df = pd.read_csv("output/laps_dataset.csv")
print(f"{len(df)} laps from {df['race'].nunique()} races")

# turn tyre compound text into 1s and 0s, one column per tyre type
df = pd.get_dummies(df, columns=["compound"], dtype=int)

compound_cols = [c for c in df.columns if c.startswith("compound_")]
feature_cols = ["tyre_life", "lap_number"] + compound_cols
X = df[feature_cols]
y = df["pace_delta_s"]

# group by race so the model never trains and tests on the same race
groups = df["race"]

print("\nTraining with Leave-One-Group-Out CV...")
print("Trains on all races except one, tests on the left out race, repeats for every race.")

logo = LeaveOneGroupOut()

baseline_errors = []
linear_errors = []
rf_errors = []
race_names = []

for train_idx, test_idx in logo.split(X, y, groups):
    X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
    y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]

    # baseline just predicts the median pace delta every time, ignores all features
    baseline = DummyRegressor(strategy="median")
    baseline.fit(X_train, y_train)
    baseline_errors.append(mean_absolute_error(y_test, baseline.predict(X_test)))

    # linear regression, simple model to compare against
    linear = LinearRegression()
    linear.fit(X_train, y_train)
    linear_errors.append(mean_absolute_error(y_test, linear.predict(X_test)))

    # random forest = lots of decision trees, averages their predictions
    rf_model = RandomForestRegressor(
        n_estimators=50,
        max_depth=10,
        random_state=42,
        n_jobs=-1  # use all cpu cores
    )
    rf_model.fit(X_train, y_train)
    rf_errors.append(mean_absolute_error(y_test, rf_model.predict(X_test)))

    # remember which race was left out this time
    race_names.append(groups.iloc[test_idx].iloc[0])

# average across all races, every race was tested unseen so this is the real score
baseline_mae = np.mean(baseline_errors)
linear_mae = np.mean(linear_errors)
rf_mae = np.mean(rf_errors)

print(f"\nBaseline MAE:      {baseline_mae:.3f} seconds")
print(f"Linear MAE:        {linear_mae:.3f} seconds")
print(f"Random Forest MAE: {rf_mae:.3f} seconds")
print(f"Random Forest improvement over baseline: {baseline_mae - rf_mae:.3f} seconds per lap")

# save per-race results so they can go in the README
results = pd.DataFrame({
    "race": race_names,
    "baseline_mae": baseline_errors,
    "linear_mae": linear_errors,
    "rf_mae": rf_errors,
})
results.to_csv("output/model_results.csv", index=False)
print("\nPer-race results saved to output/model_results.csv")

# train once on everything just to see which features the forest relied on
# (this is for understanding the model, not for the scores above)
final_model = RandomForestRegressor(n_estimators=50, max_depth=10, random_state=42, n_jobs=-1)
final_model.fit(X, y)
importances = pd.Series(final_model.feature_importances_, index=feature_cols)
print("\nFeature importance:")
print(importances.sort_values(ascending=False).round(3))