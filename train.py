import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.linear_model import LogisticRegression
import joblib

# --------------------------------------------------
# 1. Load our extracted landslide events
# --------------------------------------------------

df = pd.read_csv("data/raw/landslide_events_clean.csv")

df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

# Remove accidental header row if present
df = df[df["District"] != "District"].copy()

print("Landslide records:", len(df))

# --------------------------------------------------
# 2. Prototype environmental features
# --------------------------------------------------
# IMPORTANT:
# These are placeholders only for establishing the
# ML pipeline. They must NOT be presented as real
# measured rainfall/sensor values.
#
# Later these columns will be replaced with actual
# historical rainfall + ESP32 sensor readings.

np.random.seed(42)

n = len(df)

prototype = pd.DataFrame({
    "rain_24h": np.random.uniform(10, 100, n),
    "rain_48h": np.random.uniform(20, 180, n),
    "rain_72h": np.random.uniform(30, 250, n),
    "rain_96h": np.random.uniform(40, 320, n),
    "soil_moisture": np.random.uniform(40, 95, n),
    "tilt": np.random.uniform(0, 8, n)
})

prototype["landslide"] = 1

# --------------------------------------------------
# 3. Temporary demonstration negatives
# --------------------------------------------------
# These are ONLY for testing that the complete ML
# pipeline executes. They are NOT scientific training
# data and must be replaced before claiming accuracy.

negative = pd.DataFrame({
    "rain_24h": np.random.uniform(0, 20, n),
    "rain_48h": np.random.uniform(0, 40, n),
    "rain_72h": np.random.uniform(0, 60, n),
    "rain_96h": np.random.uniform(0, 80, n),
    "soil_moisture": np.random.uniform(10, 45, n),
    "tilt": np.random.uniform(0, 2, n),
    "landslide": 0
})

data = pd.concat([prototype, negative], ignore_index=True)

# --------------------------------------------------
# 4. Features and target
# --------------------------------------------------

X = data.drop("landslide", axis=1)
y = data["landslide"]

print("\nFinal dataset:", X.shape)
print("Classes:")
print(y.value_counts())

# --------------------------------------------------
# 5. Train/Test split
# --------------------------------------------------

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.30,
    random_state=42,
    stratify=y
)

# --------------------------------------------------
# 6. Models
# --------------------------------------------------

models = {
    "Logistic Regression": Pipeline([
        ("scaler", StandardScaler()),
        ("model", LogisticRegression(max_iter=1000))
    ]),

    "KNN": Pipeline([
        ("scaler", StandardScaler()),
        ("model", KNeighborsClassifier(n_neighbors=5))
    ]),

    "SVM": Pipeline([
        ("scaler", StandardScaler()),
        ("model", SVC())
    ]),

    "Random Forest": RandomForestClassifier(
        n_estimators=200,
        random_state=42
    ),

    "Gradient Boosting": GradientBoostingClassifier(
        random_state=42
    )
}

# --------------------------------------------------
# 7. Train + Evaluate
# --------------------------------------------------

results = []

for name, model in models.items():

    model.fit(X_train, y_train)

    predictions = model.predict(X_test)

    accuracy = accuracy_score(y_test, predictions)
    precision = precision_score(y_test, predictions, zero_division=0)
    recall = recall_score(y_test, predictions, zero_division=0)
    f1 = f1_score(y_test, predictions, zero_division=0)

    results.append([
        name,
        accuracy,
        precision,
        recall,
        f1
    ])

# --------------------------------------------------
# 8. Display results
# --------------------------------------------------

results_df = pd.DataFrame(
    results,
    columns=[
        "Model",
        "Accuracy",
        "Precision",
        "Recall",
        "F1"
    ]
)

print("\n========== MODEL RESULTS ==========")
print(results_df.to_string(index=False))

# --------------------------------------------------
# 9. Select best model by F1 score
# --------------------------------------------------

best_name = results_df.loc[
    results_df["F1"].idxmax(),
    "Model"
]

best_model = models[best_name]

print("\nBest Model:", best_name)

# --------------------------------------------------
# 10. Save model
# --------------------------------------------------

joblib.dump(best_model, "models/landslide_model.pkl")

print("\n✅ Model saved:")
print("models/landslide_model.pkl")

print("\n⚠️ DEMO NOTICE:")
print("Current negative samples are synthetic placeholders.")
print("Do NOT report these metrics as real-world accuracy.")