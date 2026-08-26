import os
import pandas as pd
from dotenv import load_dotenv
import psycopg2
from tqdm import tqdm

# ── Load environment variables from .env ──────────────────────────────
# This reads your .env file so we can use POSTGRES_USER,
# POSTGRES_PASSWORD etc without hardcoding them
load_dotenv()

# ── Connect to the database ───────────────────────────────────────────
# psycopg2 is the Python library that talks to PostgreSQL
# We build the connection using values from your .env file
conn = psycopg2.connect(
    host="fightiq-db.cd6quu8uc1xx.us-east-2.rds.amazonaws.com",       # the db is exposed to your Mac on localhost
    port=5432,
    database=os.getenv("POSTGRES_DB"),
    user=os.getenv("POSTGRES_USER"),
    password=os.getenv("POSTGRES_PASSWORD")
)

# A cursor is what you use to actually run SQL commands
cur = conn.cursor()

print("✅ Connected to database successfully")

# ── Read the CSV file ─────────────────────────────────────────────────
# pandas reads the CSV and turns it into a DataFrame
# A DataFrame is like an Excel table in your code —
# rows are fights, columns are stats
print("📂 Reading CSV file...")

df = pd.read_csv("ufc-master.csv")

# Show us what we're working with
print(f"✅ Loaded {len(df)} fights from CSV")
print(f"📊 Columns: {len(df.columns)} total")
print(f"\nFirst fight in dataset:")
print(f"  {df['R_fighter'].iloc[0]} vs {df['B_fighter'].iloc[0]}")
print(f"  Winner: {df['Winner'].iloc[0]}")
print(f"  Method: {df['finish'].iloc[0]}")
print(f"  Date:   {df['date'].iloc[0]}")

# ── Step 3: Insert fighters ───────────────────────────────────────────
# Each CSV row has TWO fighters — Red corner and Blue corner
# We need to extract each one separately and insert into fighters table
print("\n👊 Inserting fighters...")

# Keep track of fighters we already inserted
# so we don't add the same fighter twice
seen_fighters = set()

for _, row in tqdm(df.iterrows(), total=len(df), desc="Processing fighters"):

    # We'll process both corners in a loop
    for corner in ['R', 'B']:

        name = row[f'{corner}_fighter']

        # Skip if we already inserted this fighter
        if name in seen_fighters:
            continue

        seen_fighters.add(name)

        # Safely get a value — some cells in CSV are empty (NaN)
        # If empty, use None so PostgreSQL stores it as NULL
        def safe(val):
            return None if pd.isna(val) else val

        # Pull this fighter's stats from the CSV row
        height  = safe(row[f'{corner}_Height_cms'])
        reach   = safe(row[f'{corner}_Reach_cms'])
        stance  = safe(row[f'{corner}_Stance'])
        wins    = safe(row[f'{corner}_wins'])
        losses  = safe(row[f'{corner}_losses'])
        weight_class = safe(row['weight_class'])

        # Insert into fighters table
        # ON CONFLICT DO NOTHING means if the fighter already exists
        # just skip them — don't crash, don't duplicate
        cur.execute("""
            INSERT INTO fighters 
                (name, weight_class, stance, height_cm, reach_cm, wins, losses)
            VALUES 
                (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (name) DO NOTHING
        """, (name, weight_class, stance, height, reach, wins, losses))

# Save all inserts to the database
conn.commit()
print(f"✅ Inserted {len(seen_fighters)} unique fighters")
# ── Step 4: Insert fights ─────────────────────────────────────────────
# Now we insert the actual fight results
# Each row in the CSV becomes one row in the fights table
print("\n🥊 Inserting fights...")

fights_inserted = 0

for _, row in tqdm(df.iterrows(), total=len(df), desc="Processing fights"):

    def safe(val):
        return None if pd.isna(val) else val

    # Figure out the winner's actual name
    # CSV stores "Red" or "Blue" — we convert to the fighter's name
    winner_corner = safe(row['Winner'])
    if winner_corner == 'Red':
        winner = safe(row['R_fighter'])
    elif winner_corner == 'Blue':
        winner = safe(row['B_fighter'])
    else:
        winner = None  # Draw or No Contest

    cur.execute("""
        INSERT INTO fights
            (fighter1, fighter2, winner, method, 
             round, time, event_date, weight_class)
        VALUES
            (%s, %s, %s, %s, %s, %s, %s, %s)
    """, (
        safe(row['R_fighter']),
        safe(row['B_fighter']),
        winner,
        safe(row['finish']),
        safe(row['finish_round']),
        safe(row['finish_round_time']),
        safe(row['date']),
        safe(row['weight_class'])
    ))

    fights_inserted += 1

conn.commit()
print(f"✅ Inserted {fights_inserted} fights")

# ── Step 5: Generate embeddings ───────────────────────────────────────
# This is the RAG step — convert each fight into a vector
# so users can search by meaning instead of exact words
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

print("\n🤖 Generating embeddings...")

# Fetch all fights we just inserted, with their IDs
cur.execute("SELECT id, fighter1, fighter2, winner, method, round, weight_class, event_date FROM fights")
fights_to_embed = cur.fetchall()

embedded = 0

# Find which fights are already embedded so we don't redo them
cur.execute("SELECT fight_id FROM fight_embeddings")
already_embedded = set(row[0] for row in cur.fetchall())
print(f"Already embedded: {len(already_embedded)} fights — skipping those")

for fight in tqdm(fights_to_embed, desc="Embedding fights"):
    fight_id    = fight[0]

    # Skip fights we already embedded in a previous run
    if fight_id in already_embedded:
        continue
    
    fighter1    = fight[1]
    fighter2    = fight[2]
    winner      = fight[3]
    method      = fight[4]
    round_num   = fight[5]
    weight_class = fight[6]
    event_date  = fight[7]

    # Build a human readable summary of the fight
    # This is what gets converted to a vector
    # The more descriptive, the better the search results
    summary = f"{fighter1} vs {fighter2}. "

    if winner:
        summary += f"{winner} won by {method} in round {round_num}. "
    else:
        summary += f"The fight ended in a draw. "

    if weight_class:
        summary += f"This was a {weight_class} bout. "

    if event_date:
        summary += f"The fight took place on {event_date}."

    # Send the summary to OpenAI and get back 1536 numbers
    response = client.embeddings.create(
        input=summary,
        model="text-embedding-3-small"
    )

    # Extract the actual vector from the response
    embedding = response.data[0].embedding  # list of 1536 numbers

    # Store the summary and its vector in fight_embeddings
    cur.execute("""
        INSERT INTO fight_embeddings (fight_id, summary, embedding)
        VALUES (%s, %s, %s)
    """, (fight_id, summary, embedding))

    embedded += 1

    # Commit every 50 fights so we don't lose progress
    # if something goes wrong halfway through
    if embedded % 50 == 0:
        conn.commit()

# Final commit for any remaining fights
conn.commit()
print(f"✅ Generated embeddings for {embedded} fights")
print("\n🎉 Phase 2 complete! Your database is ready.")
print(f"   fighters:        2241 rows")
print(f"   fights:          7177 rows")
print(f"   fight_embeddings: {embedded} rows")

# Close the connection cleanly
cur.close()
conn.close()