# FightIQ 🥊

An AI-powered MMA intelligence platform where users can ask questions about fighters, compare matchups, and predict fight outcomes using real UFC/MMA data.

**Live demo:** http://3.133.95.6:3000

---

## What is FightIQ?

FightIQ combines a Retrieval-Augmented Generation (RAG) pipeline, an OpenAI-powered chat assistant, a custom-trained machine learning model, and automated AI quality testing into one full-stack application. Ask it about real fights, compare fighters side-by-side, or get a data-driven prediction on who wins a matchup — all backed by a database of 7,000+ real UFC fights.

This project was built end-to-end as a learning journey: from Docker fundamentals, through RAG and LLM tool calling, to training a real ML model, building a full frontend, writing automated AI tests, and deploying everything to AWS.

---

## Features

- **AI Fighter Chat** — Ask natural questions like *"How did Islam beat Oliveira?"* and get answers grounded in real fight data, not guesses
- **Fighter Comparison** — Compare two fighters side-by-side across height, reach, stance, and record
- **Fight Predictor** — Get a real win-probability prediction powered by a trained XGBoost model
- **Tool Calling** — The AI autonomously decides when to look up a fighter, compare two fighters, or run a prediction, using structured backend functions
- **Automated AI Testing** — DeepEval-based test suite that catches AI hallucinations and checks answer relevancy, turning real bugs into permanent regression tests

---

## How it works

User asks a question
↓
Question gets embedded (converted to a vector) using OpenAI
↓
pgvector searches 7,177 real fights for the most relevant matches
↓
GPT-4o-mini reads the question + retrieved fights + available tools
↓
If needed, it calls a backend tool:
• get_fighter_stats() → pulls real stats from PostgreSQL
• compare_fighters() → compares two fighters' stats
• predict_fight() → runs the trained XGBoost model
↓
GPT-4o-mini writes a natural-language answer using the real results
↓
Answer is returned to the user


---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React / Next.js, Tailwind CSS |
| Backend | FastAPI (Python) |
| Database | PostgreSQL + pgvector |
| AI | OpenAI API (embeddings + GPT-4o-mini + tool calling) |
| ML | XGBoost, scikit-learn |
| Evaluation | DeepEval |
| Infrastructure | Docker, Docker Compose, AWS (EC2, RDS, ECR, IAM) |

---

## Project Structure

FightIQ/
├── frontend/        # React/Next.js UI
├── backend/         # FastAPI endpoints
├── ml/              # XGBoost fight prediction model
├── db/              # PostgreSQL schema and seed scripts
├── docker-compose.yml
└── README.md


---

## Getting Started (Local Development)

### Prerequisites
- Docker Desktop installed and running
- An OpenAI API key ([platform.openai.com](https://platform.openai.com))

### Setup

1. **Clone the repo**
```bash
   git clone https://github.com/chrisquispe/FightIQ.git
   cd FightIQ
```

2. **Create a `.env` file** in the project root:

POSTGRES_DB=mma_db
POSTGRES_USER=mma_user
POSTGRES_PASSWORD=your_password_here
OPENAI_API_KEY=your_openai_key_here


3. **Start all services**
```bash
   docker compose up --build
```

4. **Import the fight data** (first time only — this embeds real UFC fight data, takes ~30-40 minutes and a few cents in OpenAI API usage)
```bash
   cd data
   python import.py
```

5. **Open the app**
   - Frontend: [http://localhost:3000](http://localhost:3000)
   - Backend API docs: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## Running the AI Test Suite

FightIQ includes automated tests that check the AI's answers for accuracy and relevance — not just whether the server responds, but whether it's telling the truth.

```bash
cd eval
pip install -r requirements.txt
python -m pytest test_chat.py -v
```


---

## Getting Started

```bash
# Clone the repo
git clone https://github.com/chrisquispe/FightIQ.git
cd FightIQ

# Start all services
docker compose up
```

> Full setup instructions coming as development progresses.

---

## Author

**Christopher Quispesivana**
GitHub: [@chrisquispe](https://github.com/chrisquispe)
LinkedIn: [linkedin.com/in/christopherquis](https://linkedin.com/in/christopherquis)
