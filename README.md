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

```
FightIQ/
├── frontend/          # Next.js app — chat, compare, and predict pages
│   └── app/
│       ├── chat/       # AI Q&A interface
│       ├── compare/    # Fighter comparison tool
│       ├── predict/    # Win prediction tool
│       └── components/ # Shared UI (navbar, etc.)
├── backend/            # FastAPI app
│   └── main.py          # Routes, RAG pipeline, tool calling logic
├── ml/                 # Machine learning
│   └── train.py          # XGBoost training script
├── data/                # Data pipeline
│   └── import.py          # ETL script: CSV → PostgreSQL + embeddings
├── db/                  # Database schema
│   └── init.sql            # Table definitions + pgvector setup
├── eval/                # AI quality testing
│   └── test_chat.py         # DeepEval test suite
├── docker-compose.yml
└── README.md
```


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

## The ML Model

The fight predictor is an XGBoost classifier trained on 7,019 historical UFC fights, using three engineered features: height difference, reach difference, and win-rate difference between the two fighters. It achieves **75% accuracy** on fights it never saw during training (an 80/20 train/test split).

```bash
cd ml
python train.py
```

---

## Deployment

FightIQ is deployed on AWS using:
- **EC2** — runs the containerized app
- **RDS** — managed PostgreSQL database
- **ECR** — stores the Docker images
- **IAM** — scoped access for deployment operations

---

## Known Limitations

- The prediction model doesn't currently account for head-to-head history between two specific fighters (a good next feature)
- No authentication yet — the live deployment is publicly accessible
- IP-based deployment (no permanent domain attached yet)
- Not up to date with the fights

---

## Author

**Christopher Quispesivana**
GitHub: [@chrisquispe](https://github.com/chrisquispe)
LinkedIn: [linkedin.com/in/christopherquis](https://linkedin.com/in/christopherquis)
