# Crisis Network Analysis Project

**Network Resilience in Crisis Response: Integrating Network Analysis with Social Computing and PADM Framework**

[![Python 3.13.7](https://img.shields.io/badge/python-3.13.7-blue.svg)](https://www.python.org/downloads/)

## 📖 Project Overview

This research project investigates **social behavior patterns during crisis events** through network resilience analysis, examining how information accuracy, speed of spread, and community coordination adapt when social networks face disruption. The project integrates network structural analysis with cognitive and perceptual process analysis using **LIWC (Linguistic Inquiry and Word Count)** and the enhanced **Resonance+ metric**.

### 🎯 Core Innovation
Integration of network structural analysis with cognitive process analysis using **PADM (Protective Action Decision Model)** framework to provide actionable insights for emergency managers through multi-platform data collection and analysis.

### 🏆 Key Research Questions

1. **Information Accuracy Patterns**: How does accuracy change across different platforms and cascade types?
2. **Multi-Platform Speed vs. Accuracy Trade-offs**: Do different platforms exhibit distinct speed-accuracy characteristics?
3. **Community Coordination Evolution**: How do Reddit communities reorganize during crises compared to Twitter networks?
4. **Cross-Crisis and Cross-Platform Patterns**: What behavioral patterns are consistent across crisis types AND platforms?

## 🔬 Crisis Events Being Analyzed

### 1. Los Angeles Wildfires (January 7-31, 2025)
- **Type**: Natural disaster with celebrity involvement
- **Impact**: 30+ deaths, 200,000+ evacuations, 18,000+ structures destroyed
- **Keywords**: `#PalisadesFire`, `#EatonFire`, `#LAFires`
- **Reddit Subreddits**: `r/LosAngeles`, `r/California`, `r/wildfire`

### 2. India-Pakistan Conflict (May 7-31, 2025)
- **Type**: Political/military crisis with competing narratives
- **Timeline**: Pahalgam attack → Operation Sindoor → diplomatic resolution
- **Keywords**: `#IndiaPakistanConflict`, `#OperationSindoor`
- **Reddit Subreddits**: `r/india`, `r/pakistan`, `r/Kashmir`, `r/worldnews`

### 3. Turkey-Syria Earthquake (February 6-20, 2023)
- **Type**: International natural disaster with cross-linguistic data
- **Impact**: 50,000+ fatalities, international rescue operations
- **Keywords**: `#TurkeyEarthquake`, `#SyriaEarthquake`, `#DepremTurkiye`
- **Reddit Subreddits**: `r/Turkey`, `r/syria`, `r/earthquake`

## 🏗️ Project Structure

```
crisis-network-analysis/
├── src/
│   ├── collection/           # Data collection modules
│   │   ├── reddit_collector.py
│   │   ├── enhanced_reddit_collector_v2.py
│   │   └── multi_platform_collector.py
│   ├── preprocessing/        # Data preprocessing and cleaning
│   │   ├── data_cleaner.py
│   │   └── quality_validator.py
│   ├── networks/            # Network construction and analysis
│   │   ├── crisis_network_analyzer.py
│   │   └── multi_layer_networks.py
│   ├── social_computing/    # PADM and cognitive analysis
│   │   ├── padm_analyzer.py
│   │   ├── liwc_processor.py
│   │   └── resonance_calculator.py
│   ├── visualization/       # Network and data visualization
│   │   └── crisis_visualizer.py
│   └── utils/              # Utility functions
│       ├── config_loader.py
│       └── logger.py
├── config/
│   ├── crisis_events.yaml
│   ├── analysis_params.yaml
│   └── api_keys.env.template
├── data/
│   ├── raw/                # Raw collected data (gitignored)
│   ├── processed/          # Processed datasets (gitignored)
│   ├── networks/           # Network data files
│   └── results/            # Analysis results
├── notebooks/              # Jupyter notebooks for analysis
├── tests/                  # Unit tests
├── docs/                   # Documentation
├── docker/                 # Docker configuration
└── requirements.txt
```

## 🚀 Quick Start

### Prerequisites

- **Operating System**: Garuda Linux (or any Linux distribution)
- **Shell**: Fish shell recommended (bash also supported)
- **Python**: 3.13.7+
- **Git**: Latest version

### Installation

1. **Clone the repository**
   ```fish
   git clone https://github.com/yourusername/crisis-network-analysis.git
   cd crisis-network-analysis
   ```

2. **Create and activate virtual environment**
   ```fish
   python -m venv venv
   source venv/bin/activate.fish  # For fish shell
   # source venv/bin/activate     # For bash shell
   ```

3. **Install dependencies**
   ```fish
   pip install -r requirements.txt
   ```

4. **Set up configuration**
   ```fish
   cp config/api_keys.env.template config/api_keys.env
   # Edit config/api_keys.env with your API credentials
   ```

5. **Verify installation**
   ```fish
   python -c "import src.utils.config_loader; print('✅ Setup complete!')"
   ```

## 📊 Core Technologies & Frameworks

### Data Collection
- **Reddit API (praw)**: Primary data source (40% of data)
- **Academic Datasets**: Historical crisis data (30% of data)  
- **News APIs**: Contextual information (30% of data)

### Network Analysis
- **NetworkX 3.5**: Multi-layer network construction
- **Pandas 2.3.2**: Data manipulation and analysis
- **NumPy 2.3.2**: Numerical computations

### Cognitive Analysis
- **LIWC**: Linguistic Inquiry and Word Count processing
- **scikit-learn**: Machine learning for community detection
- **Custom Resonance+ Calculator**: Enhanced metric implementation

### Visualization
- **Matplotlib/Seaborn**: Statistical visualizations
- **Plotly**: Interactive network visualizations
- **D3.js**: Advanced web-based visualizations

## 🔧 Enhanced Resonance+ Metric

The **Resonance+** metric combines pre-decision processes of PADM with collective attention:

```python
class MultiPlatformResonancePlus:
    def calculate_resonance_plus(self, post_data, platform):
        weights = self.platform_weights[platform]
        return {
            'novelty': weights['novelty'] * self._calculate_novelty(post_data),
            'persistence': weights['persistence'] * self._calculate_persistence(post_data),
            'crisis_relevance': weights['crisis_relevance'] * self._calculate_relevance(post_data),
            'cognitive_resonance': weights['cognitive'] * self._calculate_cognitive_resonance(post_data)
        }
```

### Key Components:
1. **In-conversation Novelty**: Information uniqueness within discussion threads
2. **Local Persistence**: How long information remains active in communities
3. **Crisis Relevance**: Domain-specific importance scoring
4. **Cognitive Resonance**: LIWC-based emotional and cognitive processing indicators

## 📈 PADM Framework Integration

The **Protective Action Decision Model (PADM)** integration analyzes pre-decision processes:

```python
class PADMFramework:
    def analyze_predecision_processes(self, posts_df, user_networks):
        return {
            'exposure': self.exposure_analyzer.calculate_exposure(posts_df, user_networks),
            'attention': self.attention_tracker.track_collective_attention(posts_df),
            'comprehension': self.comprehension_assessor.assess_comprehension(posts_df)
        }
```

## 🧪 Multi-Layer Network Analysis

The project constructs and analyzes multiple network layers:

1. **User Networks**: Interaction patterns between users
2. **Content Networks**: Information flow and content similarity
3. **Temporal Networks**: Time-based evolution of discussions
4. **Geographic Networks**: Location-based information spread
5. **Semantic Networks**: Topic and keyword relationships
6. **Cognitive Networks**: LIWC-based emotional/cognitive connections

## 📋 Hub Classification System

Six types of influential users are identified:

1. **Structural Hubs**: High degree centrality users
2. **Cognitive Influencers**: High LIWC-based emotional resonance
3. **Information Brokers**: Bridge different communities
4. **Resonance Leaders**: High Resonance+ scores
5. **Crisis Specialists**: Domain expertise indicators
6. **Community Coordinators**: Facilitate group coordination

## 🔍 Data Quality & Validation

### Quality Assurance
- **Automated filtering**: Spam and low-quality content removal
- **Relevance scoring**: Crisis-specific content validation
- **Duplicate detection**: Cross-platform deduplication
- **Multi-source validation**: Academic dataset cross-verification

### Statistical Robustness
- **Bootstrap analysis**: Across all data sources
- **Cross-platform consistency**: Pattern validation
- **Temporal validation**: Multiple time periods
- **Expert review**: Emergency management validation

## 📦 Usage Examples

### Basic Data Collection
```python
from src.collection.enhanced_reddit_collector_v2 import EnhancedRedditCrisisCollector

# Initialize collector
collector = EnhancedRedditCrisisCollector()

# Collect data for Los Angeles Wildfires
la_fires_data = collector.collect_crisis_data("los_angeles_wildfires_2025")
print(f"Collected {len(la_fires_data)} posts")
```

### Network Analysis
```python
from src.networks.crisis_network_analyzer import CrisisNetworkAnalyzer

# Initialize analyzer
analyzer = CrisisNetworkAnalyzer("data/processed/master_dataset.csv")

# Build multi-layer networks
networks = analyzer.build_multi_layer_networks()

# Calculate network metrics
metrics = analyzer.calculate_network_metrics()
```

### Resonance+ Calculation
```python
from src.social_computing.resonance_calculator import MultiPlatformResonancePlus

# Initialize calculator
resonance_calc = MultiPlatformResonancePlus()

# Calculate resonance for a post
resonance_score = resonance_calc.calculate_resonance_plus(post_data, "reddit")
```

**Target**: 90%+ test coverage across all modules

## 📊 Expected Performance Metrics

### Technical Metrics
- **Processing Speed**: 50k+ posts in <10 minutes
- **Data Collection**: 500k+ posts across all sources
- **Prediction Accuracy**: >75% accuracy in crisis phase prediction
- **Test Coverage**: 90%+ across all modules

### Research Metrics
- **Statistical Significance**: p < 0.05 with multiple comparison corrections
- **Cross-Crisis Validation**: Patterns consistent across 3+ crisis types
- **Multi-Platform Robustness**: Results replicated across Reddit, academic, and news data

## 📋 API Configuration

### Reddit API Setup
1. Create Reddit application at https://www.reddit.com/prefs/apps
2. Add credentials to `config/api_keys.env`:
   ```
   REDDIT_CLIENT_ID=your_client_id
   REDDIT_CLIENT_SECRET=your_client_secret
   REDDIT_USER_AGENT=Crisis Network Analysis Research v1.0
   ```

### Alternative APIs (Optional)
- **NewsAPI**: For contextual news data
- **Guardian API**: Additional news source
- **Academic APIs**: Dataset access tokens

## 🐳 Docker Support

Build and run with Docker:
```fish
# Build image
docker build -t crisis-network-analysis .

# Run container
docker run -v $(pwd)/data:/app/data crisis-network-analysis

# Run with Jupyter
docker run -p 8888:8888 crisis-network-analysis jupyter lab
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Setup for Contributors
```fish
# Install development dependencies
pip install -r requirements-dev.txt

# Install pre-commit hooks
pre-commit install

# Run code formatting
black src/ tests/
isort src/ tests/

# Run linting
flake8 src/ tests/
```

## 🙏 Acknowledgments

- **PADM Framework**: Based on Lindell & Perry's Protective Action Decision Model
- **Resonance+ Metric**: Enhanced from Wang & Kogan's original resonance concept
- **LIWC Integration**: Using Linguistic Inquiry and Word Count 2015
- **Crisis Informatics**: Building on established crisis communication research
