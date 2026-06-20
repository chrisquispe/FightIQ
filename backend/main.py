import os
from fastapi import FastAPI
from dotenv import load_dotenv
import psycopg2
from pydantic import BaseModel
from openai import OpenAI
import json
import joblib

# Load the trained XGBoost model once when the app starts
# Loading it inside every request would be slow — load once, reuse forever
fight_model = joblib.load("fight_predictor.pkl")


load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# This creates your FastAPI application
# Everything you build gets attached to this "app" object
app = FastAPI(title="FightIQ API")

# This defines what the /chat request body must look like
# Frontend must send: { "question": "some text" }
class ChatRequest(BaseModel):
    question: str

# ── Tool definitions ──────────────────────────────────────────────────
# This is how we describe our Python functions to GPT-4
# GPT-4 reads the "description" to decide WHEN to use each tool
# and reads "parameters" to know WHAT arguments to send
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_fighter_stats",
            "description": "Get detailed stats for a single UFC fighter, "
                            "including height, reach, stance, wins, and losses.",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "The fighter's full name, e.g. 'Islam Makhachev'"
                    }
                },
                "required": ["name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "compare_fighters",
            "description": "Compare two UFC fighters side by side across "
                            "height, reach, stance, wins, and losses.",
            "parameters": {
                "type": "object",
                "properties": {
                    "name1": {
                        "type": "string",
                        "description": "The first fighter's full name"
                    },
                    "name2": {
                        "type": "string",
                        "description": "The second fighter's full name"
                    }
                },
                "required": ["name1", "name2"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "predict_fight",
            "description": "Predict the win probability between two UFC "
                            "fighters using a trained machine learning model "
                            "based on height, reach, and win rate differences.",
            "parameters": {
                "type": "object",
                "properties": {
                    "name1": {
                        "type": "string",
                        "description": "The first fighter's full name"
                    },
                    "name2": {
                        "type": "string",
                        "description": "The second fighter's full name"
                    }
                },
                "required": ["name1", "name2"]
            }
        }
    }
]

# ── Actual tool functions ───────────────────────────────────────────
# These are the REAL Python functions that run when GPT-4
# decides to call a tool. They do the actual work.

def get_fighter_stats(name: str):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT name, weight_class, stance, height_cm, reach_cm, wins, losses
        FROM fighters WHERE name ILIKE %s
    """, (name,))
    result = cur.fetchone()
    cur.close()
    conn.close()

    if result is None:
        return {"error": f"Fighter '{name}' not found"}

    return {
        "name": result[0],
        "weight_class": result[1],
        "stance": result[2],
        "height_cm": float(result[3]) if result[3] is not None else None,
        "reach_cm": float(result[4]) if result[4] is not None else None,
        "wins": result[5],
        "losses": result[6]
    }


def compare_fighters(name1: str, name2: str):
    fighter1 = get_fighter_stats(name1)
    fighter2 = get_fighter_stats(name2)
    return {"fighter1": fighter1, "fighter2": fighter2}

def predict_fight(name1: str, name2: str):
    fighter1 = get_fighter_stats(name1)
    fighter2 = get_fighter_stats(name2)

    if "error" in fighter1 or "error" in fighter2:
        return {"error": "One or both fighters not found"}

    # Build the exact same features the model was trained on
    height_diff = fighter1["height_cm"] - fighter2["height_cm"]
    reach_diff = fighter1["reach_cm"] - fighter2["reach_cm"]

    f1_win_rate = fighter1["wins"] / (fighter1["wins"] + fighter1["losses"])
    f2_win_rate = fighter2["wins"] / (fighter2["wins"] + fighter2["losses"])
    win_rate_diff = f1_win_rate - f2_win_rate

    # XGBoost expects a 2D array — one row, three columns
    # This matches the exact feature order used during training
    features = [[height_diff, reach_diff, win_rate_diff]]

    # predict_proba returns probabilities for BOTH outcomes: [P(lose), P(win)]
    # We want index [1] — the probability that fighter1 wins
    probabilities = fight_model.predict_proba(features)
    fighter1_win_prob = probabilities[0][1]
    fighter2_win_prob = 1 - fighter1_win_prob

    return {
        "fighter1": name1,
        "fighter2": name2,
        "fighter1_win_probability": round(float(fighter1_win_prob), 3),
        "fighter2_win_probability": round(float(fighter2_win_prob), 3)
    }


# A helper function to get a database connection
# We'll call this every time a route needs to talk to the database
def get_db_connection():
    return psycopg2.connect(os.getenv("DATABASE_URL"))


# ── Route 1: health check ───────────────────────────────────────────
# A simple GET route to confirm the API is alive
# No database, no data needed — just a sanity check
@app.get("/health")
def health_check():
    return {"status": "ok", "message": "FightIQ API is running"}


# ── Route 2: get one fighter ────────────────────────────────────────
# GET route — name comes from the URL itself
# Example: GET /fighters/Islam Makhachev
@app.get("/fighters/{name}")
def get_fighter(name: str):
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT name, weight_class, stance, height_cm, reach_cm, 
               wins, losses, draws
        FROM fighters
        WHERE name ILIKE %s
    """, (name,))

    result = cur.fetchone()
    cur.close()
    conn.close()

    if result is None:
        return {"error": f"Fighter '{name}' not found"}

    return {
        "name": result[0],
        "weight_class": result[1],
        "stance": result[2],
        "height_cm": result[3],
        "reach_cm": result[4],
        "wins": result[5],
        "losses": result[6],
        "draws": result[7]
    }
# ── Route 3: chat (RAG pipeline) ────────────────────────────────────
# POST route — receives a question, returns an AI answer
# grounded in real fight data from our database
@app.post("/chat")
def chat(request: ChatRequest):
    question = request.question

    # ── Step 1: Embed + search (same as before) ──────────────────────
    embedding_response = client.embeddings.create(
        input=question,
        model="text-embedding-3-small"
    )
    question_vector = embedding_response.data[0].embedding

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT summary FROM fight_embeddings
        ORDER BY embedding <-> %s::vector
        LIMIT 5
    """, (question_vector,))
    results = cur.fetchall()
    cur.close()
    conn.close()

    relevant_fights = [row[0] for row in results]
    context = "\n".join(relevant_fights)

    # ── Step 2: Send question + context + AVAILABLE TOOLS to GPT-4 ───
    messages = [
        {
            "role": "system",
            "content": "You are FightIQ, an MMA expert assistant. "
                        "Use the fight data provided when relevant. "
                        "Use the available tools when the user asks "
                        "about specific fighter stats or comparisons."
        },
        {
            "role": "user",
            "content": f"Fight data:\n{context}\n\nQuestion: {question}"
        }
    ]

    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        tools=tools  # ← this is new: we hand GPT-4 the tool list
    )

    response_message = completion.choices[0].message

    # ── Step 3: Check if GPT-4 wants to call a tool ───────────────────
    if response_message.tool_calls:

        # GPT-4 can request multiple tool calls — loop through all of them
        messages.append(response_message)

        for tool_call in response_message.tool_calls:
            function_name = tool_call.function.name
            function_args = json.loads(tool_call.function.arguments)

            # Call the actual matching Python function
            if function_name == "get_fighter_stats":
                result = get_fighter_stats(**function_args)
            elif function_name == "compare_fighters":
                result = compare_fighters(**function_args)
            elif function_name == "predict_fight":
                result = predict_fight(**function_args)
            else:
                result = {"error": "Unknown tool"}

            # Add the tool's result back into the conversation
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": json.dumps(result)
            })

        # ── Step 4: Ask GPT-4 again, now WITH the tool results ────────
        # This second call lets GPT-4 write a natural language answer
        # using the real data the tool returned
        second_completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages
        )
        answer = second_completion.choices[0].message.content

    else:
        # GPT-4 didn't need a tool — just answer from the fight data
        answer = response_message.content

    return {
        "question": question,
        "answer": answer,
        "sources": relevant_fights
    }