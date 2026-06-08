# FightIQ 🥊
An AI-powered MMA intelligence platform where users can ask questions about fighters, compare matchups, and predict fight outcomes using real UFC/MMA data.

> 🚧 **Currently in development**

---

## Features

- **AI Fighter Chat** — Ask questions like "How did Islam beat Oliveira?" using RAG over real fight data
- **Fighter Comparison** — Compare two fighters across striking, wrestling, reach, and recent activity
- **Fight Predictor** — ML-based win probability prediction using historical fighter stats
- **MCP Tool Calling** — AI can call structured tools like `get_fighter_stats()`, `compare_fighters()`, and `predict_fight()`
- **AI Quality Testing** — DeepEval integration to test for hallucinations, relevance, and answer accuracy

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React / Next.js |
| Backend | FastAPI |
| Database | PostgreSQL + pgvector |
| AI | OpenAI API |
| ML | XGBoost / scikit-learn |
| Evaluation | DeepEval |
| Infrastructure | Docker + Docker Compose |

---

## Project Structure

```
FightIQ/
├── frontend/        # React/Next.js UI
├── backend/         # FastAPI endpoints
├── ml/              # XGBoost fight prediction model
├── db/              # PostgreSQL schema and seed scripts
├── docker-compose.yml
└── README.md
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
- GitHub: [@chrisquispe](https://github.com/chrisquispe)
- LinkedIn: [linkedin.com/in/christopherquis](https://linkedin.com/in/christopherquis)