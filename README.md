# Crisis Network Analysis

**Multi-layer social network analysis platform for crisis events — detecting community structure, information flow, and behavioral patterns at scale.**

[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/dashboard-streamlit-FF4B4B.svg)](https://streamlit.io)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

## What It Does

- Builds **4 simultaneous network layers** (user interactions, content flow, temporal evolution, semantic similarity) from Reddit crisis data
- Detects community structure using **Louvain community detection**
- Scores content influence with the novel **Resonance+** metric — combining novelty, persistence, crisis relevance, and linguistic signals
- Classifies influential nodes into **6 hub types**: Structural Hubs, Information Brokers, Resonance Leaders, Cognitive Influencers, Crisis Specialists, and Community Coordinators
- Runs **LIWC linguistic analysis** across crisis timelines to surface cognitive and emotional shifts in community language
- Delivers results through an interactive **Streamlit dashboard** with network visualizations, temporal charts, and exportable reports

## Crisis Events Analyzed

| Event | Period | Scale |
|---|---|---|
| **LA Wildfires** | Jan 7–31, 2025 | 30+ deaths · 200k+ evacuations · `r/LosAngeles`, `r/wildfire` |
| **Turkey-Syria Earthquake** | Feb 6–20, 2023 | 50k+ fatalities · international response · `r/Turkey`, `r/syria` |

## Tech Stack

| Layer | Libraries |
|---|---|
| Network Analysis | NetworkX 3.5, python-louvain |
| Data | Pandas 2.3, NumPy 2.3, PRAW (Reddit API) |
| NLP / Linguistics | LIWC, scikit-learn |
| Dashboard | Streamlit, Plotly |
| Infrastructure | Docker, pytest |

## Key Features

**Multi-Layer Networks**
- **User Network** — reply/mention interaction graph
- **Content Network** — information flow and repost cascades
- **Temporal Network** — time-sliced evolution of discussion
- **Semantic Network** — keyword and topic co-occurrence

**Resonance+ Metric**
Scores each post across four weighted dimensions: in-conversation novelty, local persistence, crisis domain relevance, and LIWC-derived cognitive resonance. Surfaces high-impact content beyond simple engagement counts.

**Hub Classification**
Louvain community detection + centrality analysis classifies users into 6 functional roles, enabling targeted analysis of how information gatekeepers behave across different crisis phases.

## Quick Start

```bash
git clone https://github.com/yourusername/crisis-network-analysis.git
cd crisis-network-analysis

python -m venv venv && source venv/bin/activate
pip install -r requirements.txt

cp config/api_keys.env.template config/api_keys.env
# Add your Reddit API credentials to config/api_keys.env

streamlit run dashboard/app.py        # Launch dashboard
python scripts/test_setup.py          # Verify installation
```

**Docker:**
```bash
docker build -t crisis-network-analysis .
docker run -p 8501:8501 -v $(pwd)/data:/app/data crisis-network-analysis
```

## Architecture

```
src/
├── collection/       # Reddit API data collection
├── preprocessing/    # Cleaning, deduplication, quality scoring
├── networks/         # Multi-layer network construction & metrics
├── social_computing/ # Resonance+ calculator, LIWC processor
├── visualization/    # Plot generation
└── utils/            # Config, logging

dashboard/            # Streamlit app (6 analysis pages)
config/               # Crisis event definitions, analysis params
data/                 # raw/ · processed/ · networks/ · results/
```

## Contributing

```bash
pip install -r requirements-dev.txt
pre-commit install
pytest tests/                         # Run test suite
black src/ tests/ && isort src/ tests/
```

1. Fork → feature branch → PR
2. All PRs require passing tests and `black`/`isort` formatting
