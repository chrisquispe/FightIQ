import os
import pandas as pd
import psycopg2
from dotenv import load_dotenv

load_dotenv()

# ── Connect and pull ALL fight + fighter data ─────────────────────────
# We need both tables joined together so each row has
# everything about BOTH fighters in that fight
conn = psycopg2.connect(
    host="localhost",
    port=5432,
    database=os.getenv("POSTGRES_DB"),
    user=os.getenv("POSTGRES_USER"),
    password=os.getenv("POSTGRES_PASSWORD")
)

print("📂 Loading fight + fighter data...")

query = """
    SELECT 
        f.fighter1, f.fighter2, f.winner,
        f1.height_cm AS f1_height, f1.reach_cm AS f1_reach,
        f1.wins AS f1_wins, f1.losses AS f1_losses,
        f2.height_cm AS f2_height, f2.reach_cm AS f2_reach,
        f2.wins AS f2_wins, f2.losses AS f2_losses
    FROM fights f
    JOIN fighters f1 ON f.fighter1 = f1.name
    JOIN fighters f2 ON f.fighter2 = f2.name
    WHERE f.winner IS NOT NULL
"""

df = pd.read_sql(query, conn)
conn.close()

print(f"✅ Loaded {len(df)} fights with complete fighter data")
print(df.head())

# ── Feature engineering ───────────────────────────────────────────────
# XGBoost needs DIFFERENCES between fighters, not raw stats.
# "fighter1 is 5cm taller" matters more than "fighter1 is 180cm"
print("\n🔧 Engineering features...")

df['height_diff'] = df['f1_height'] - df['f2_height']
df['reach_diff']  = df['f1_reach']  - df['f2_reach']

# Win rate instead of raw win count — fairer comparison
# A 10-2 record (83% win rate) is better than a 10-8 record (56%)
# even though both have 10 wins
df['f1_win_rate'] = df['f1_wins'] / (df['f1_wins'] + df['f1_losses'])
df['f2_win_rate'] = df['f2_wins'] / (df['f2_wins'] + df['f2_losses'])
df['win_rate_diff'] = df['f1_win_rate'] - df['f2_win_rate']

# ── Step: build the TARGET column ─────────────────────────────────────
# XGBoost needs a number to predict, not text like "Joe Pyfer"
# We convert winner into: 1 if fighter1 won, 0 if fighter2 won
df['fighter1_won'] = (df['winner'] == df['fighter1']).astype(int)

# ── Step: drop rows with missing data ─────────────────────────────────
# Some fighters might be missing height/reach data (NULL in database)
# XGBoost can't train on missing values, so we remove those rows
feature_columns = ['height_diff', 'reach_diff', 'win_rate_diff']
df_clean = df.dropna(subset=feature_columns + ['fighter1_won'])

print(f"✅ {len(df_clean)} fights ready for training (dropped {len(df) - len(df_clean)} with missing data)")
print(df_clean[['fighter1', 'fighter2', 'height_diff', 'reach_diff', 'win_rate_diff', 'fighter1_won']].head())

# ── Train/test split ───────────────────────────────────────────────────
# We never train AND test on the same data — that would be cheating.
# Split: 80% for training, 20% held back to test on unseen fights
from sklearn.model_selection import train_test_split

X = df_clean[feature_columns]      # the inputs (height_diff, reach_diff, win_rate_diff)
y = df_clean['fighter1_won']       # the answer key (1 or 0)

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

print(f"\n📊 Training set: {len(X_train)} fights")
print(f"📊 Test set: {len(X_test)} fights")

# ── Train the XGBoost model ─────────────────────────────────────────────
import xgboost as xgb

print("\n🤖 Training XGBoost model...")

model = xgb.XGBClassifier(
    n_estimators=100,      # number of decision trees to build
    max_depth=4,           # how deep each tree can go (prevents overfitting)
    learning_rate=0.1,     # how aggressively the model learns each step
    random_state=42
)

model.fit(X_train, y_train)

print("✅ Model trained")

# ── Evaluate accuracy ────────────────────────────────────────────────────
from sklearn.metrics import accuracy_score

predictions = model.predict(X_test)
accuracy = accuracy_score(y_test, predictions)

print(f"\n🎯 Test accuracy: {accuracy:.2%}")

# ── Save the trained model ──────────────────────────────────────────────
import joblib

print("\n💾 Saving model...")

joblib.dump(model, "fight_predictor.pkl")

print("✅ Model saved as fight_predictor.pkl")