# Methodology Documentation

Comprehensive research methodology for the Crisis Network Analysis project.

## Table of Contents

1. [Research Framework](#research-framework)
2. [Data Collection Methodology](#data-collection-methodology)
3. [Data Preprocessing](#data-preprocessing)
4. [Network Analysis](#network-analysis)
5. [PADM Integration](#padm-integration)
6. [LIWC Analysis](#liwc-analysis)
7. [Quality Assurance](#quality-assurance)
8. [Ethical Considerations](#ethical-considerations)

---

## Research Framework

### Theoretical Foundation

This project integrates three major frameworks for crisis communication analysis:

1. **Network Resilience Theory**
   - Examines how social networks maintain functionality during disruptions
   - Analyzes structural adaptations and recovery patterns
   - Identifies critical nodes and connections

2. **Protective Action Decision Model (PADM)**
   - Framework for understanding pre-decision processes during crises
   - Three core components:
     - **Exposure**: Information exposure patterns
     - **Attention**: Collective attention dynamics
     - **Comprehension**: Understanding and interpretation of crisis information

3. **Linguistic Inquiry and Word Count (LIWC)**
   - Psycholinguistic analysis of text content
   - Measures cognitive and emotional processes
   - Identifies behavioral patterns through language

### Research Questions

1. **Information Accuracy Patterns**: How does accuracy change across different crisis phases?
2. **Speed vs. Accuracy Trade-offs**: What are the temporal dynamics of information quality?
3. **Community Coordination Evolution**: How do communities reorganize during crises?
4. **Cross-Crisis Patterns**: What behavioral patterns are consistent across crisis types?

---

## Data Collection Methodology

### Data Sources

#### Primary Source: Reddit
- **Coverage**: 40% of total data
- **Rationale**:
  - Threaded discussions enable conversation analysis
  - Community-based organization
  - Publicly accessible with ethical API access
  - Temporal metadata available

#### Secondary Sources (Planned)
- **News APIs**: 30% - Contextual validation and timeline anchoring
- **Academic Datasets**: 30% - Historical crisis data for comparison

### Collection Strategy

#### 1. Crisis Event Selection Criteria
Events must meet the following criteria:
- Significant social impact (documented through media coverage)
- Sufficient social media activity (minimum 1,000 posts)
- Clear temporal boundaries (identifiable start and end)
- Public interest (not sensitive/classified information)

#### 2. Reddit Collection Parameters

**Subreddit Selection:**
- Primary: Crisis-specific subreddits (e.g., r/wildfire)
- Geographic: Location-based subreddits (e.g., r/LosAngeles)
- General: Broad discussion forums (e.g., r/worldnews)

**Temporal Windows:**
- Pre-crisis: 7 days before event start
- Acute phase: During active crisis
- Response phase: Immediate aftermath
- Recovery phase: Extended recovery period

**Post Filtering:**
- Keyword matching (crisis-specific terms)
- Relevance scoring (content similarity)
- Temporal filtering (within crisis time bounds)
- Quality filtering (minimum engagement threshold)

#### 3. Data Collection Protocol

```python
# Standard collection workflow
1. Load crisis configuration from YAML
2. Initialize Reddit collector with API credentials
3. For each subreddit:
   a. Collect posts using keyword search
   b. Collect posts using time-based filtering
   c. Collect comment threads for high-engagement posts
4. Deduplicate across subreddits
5. Save raw data with crisis_id tag
6. Generate collection report
```

### Rate Limiting and API Ethics

- Respect Reddit API rate limits (1 request per second)
- Implement exponential backoff for errors
- Use read-only authentication
- No manipulation of vote counts or comments
- No scraping of private/restricted content

---

## Data Preprocessing

### Stage 1: Data Cleaning

**Implemented in:** `src/preprocessing/data_cleaner.py`

1. **Duplicate Removal**
   - Exact content duplicates
   - Cross-subreddit duplicates
   - Repost detection

2. **Content Filtering**
   - Remove deleted/removed posts
   - Filter bot-generated content
   - Remove spam and low-quality posts

3. **Text Normalization**
   - Whitespace normalization
   - Special character handling
   - Encoding standardization

4. **Missing Value Handling**
   - Fill missing text fields with empty strings
   - Fill missing numeric fields with 0
   - Document missing data patterns

5. **Outlier Detection**
   - Statistical outlier removal (IQR method)
   - Content length validation
   - Engagement metric validation

### Stage 2: Quality Validation

**Implemented in:** `src/preprocessing/quality_validator.py`

1. **Completeness Assessment**
   - Required column presence
   - Missing value rates
   - Data coverage metrics

2. **Consistency Checks**
   - Timestamp validation
   - Score consistency
   - Ratio validation (upvote_ratio between 0-1)

3. **Temporal Coverage**
   - Date range analysis
   - Gap identification
   - Temporal distribution assessment

4. **Content Quality**
   - Average content length
   - Spam indicator detection
   - Language consistency

5. **Overall Quality Score**
   - Weighted combination of all metrics
   - Threshold: Minimum 60/100 for analysis
   - Documentation of quality issues

---

## Network Analysis

### Multi-Layer Network Construction

**Implemented in:** `src/networks/crisis_network_analyzer.py`

#### Layer 1: User Interaction Network
- **Nodes**: Reddit users
- **Edges**: Reply relationships, mentions, common subreddit participation
- **Weight**: Number of interactions
- **Purpose**: Identify influential users and community structure

#### Layer 2: Content Similarity Network
- **Nodes**: Posts
- **Edges**: TF-IDF cosine similarity > threshold
- **Weight**: Similarity score
- **Purpose**: Track information propagation and duplicate detection

#### Layer 3: Temporal Network
- **Nodes**: Posts
- **Edges**: Temporal proximity (within time window)
- **Weight**: Inverse time difference
- **Purpose**: Understand temporal dynamics of discussion

#### Layer 4: Subreddit Co-occurrence Network
- **Nodes**: Subreddits
- **Edges**: User overlap
- **Weight**: Number of shared users
- **Purpose**: Identify cross-community information flow

### Network Metrics

#### Node-Level Metrics
1. **Degree Centrality**: Number of connections
2. **Betweenness Centrality**: Bridge between communities
3. **Closeness Centrality**: Access to information
4. **PageRank**: Overall influence
5. **Clustering Coefficient**: Local connectivity

#### Network-Level Metrics
1. **Density**: Overall connectedness
2. **Average Path Length**: Information spread speed
3. **Diameter**: Maximum distance between nodes
4. **Modularity**: Community structure strength
5. **Assortativity**: Homophily patterns

### Hub Classification

Six types of influential users identified:

1. **Structural Hubs**: High degree centrality (top 10%)
2. **Information Brokers**: High betweenness (bridge communities)
3. **Cognitive Influencers**: High LIWC emotional resonance
4. **Resonance Leaders**: High Resonance+ scores
5. **Crisis Specialists**: Domain-specific expertise
6. **Community Coordinators**: Facilitate group coordination

---

## PADM Integration

### Pre-Decision Process Analysis

**Implemented in:** `src/liwc_integration.py`

#### Component 1: Information Exposure
**Measurement:**
- Post reach (views, engagement)
- Subreddit coverage
- Temporal distribution

**Metrics:**
- Exposure rate: Posts per hour during peak
- Coverage breadth: Number of subreddits
- Audience size: Unique users exposed

#### Component 2: Collective Attention
**Measurement:**
- Comment volume
- Reply depth
- Time spent in threads

**Metrics:**
- Attention intensity: Comments per post
- Attention duration: Thread lifespan
- Attention focus: Topic concentration

#### Component 3: Comprehension Assessment
**Measurement:**
- LIWC cognitive processes
- Question-answer patterns
- Information clarification requests

**Metrics:**
- Comprehension indicators: Cognitive process words
- Uncertainty levels: Tentative language
- Clarification-seeking: Question marks, help requests

---

## LIWC Analysis

### Cognitive Process Categories

**Based on LIWC 2015 Dictionary**

1. **Cognitive Processes** (cogproc)
   - Words: think, know, consider, understand
   - Purpose: Measure analytical thinking

2. **Causation**
   - Words: because, cause, due, since
   - Purpose: Understand reasoning patterns

3. **Certainty**
   - Words: sure, certain, definitely
   - Purpose: Measure confidence levels

4. **Insight**
   - Words: understand, realize, see
   - Purpose: Track comprehension moments

5. **Tentative**
   - Words: maybe, perhaps, might
   - Purpose: Identify uncertainty

### Emotional Process Categories

1. **Positive Emotion** (posemo)
   - Purpose: Measure hope, optimism

2. **Negative Emotion** (negemo)
   - Purpose: Measure fear, worry, anger

3. **Anxiety** (anx)
   - Purpose: Specific crisis-related anxiety

4. **Anger**
   - Purpose: Frustration and conflict

5. **Sadness**
   - Purpose: Grief and loss

### Behavioral Categories

1. **Risk** - Danger awareness
2. **Social** - Community orientation
3. **Time** - Temporal awareness
4. **Space** - Spatial awareness
5. **Motion** - Action orientation

### Resonance+ Metric

**Enhanced metric combining PADM with collective attention:**

```
Resonance+ = w1 * Novelty + w2 * Persistence + w3 * Relevance + w4 * Cognitive_Resonance

Where:
- Novelty: Information uniqueness in conversation
- Persistence: Duration of attention
- Relevance: Crisis-specific importance
- Cognitive_Resonance: LIWC-based emotional/cognitive indicators
- w1, w2, w3, w4: Platform-specific weights
```

---

## Quality Assurance

### Data Quality Standards

1. **Minimum Quality Thresholds**
   - Overall quality score: 60/100
   - Completeness: 80% of required fields
   - Consistency: <5% invalid records
   - Temporal coverage: <10% gaps

2. **Validation Checkpoints**
   - Post-collection validation
   - Post-cleaning validation
   - Pre-analysis validation

3. **Documentation Requirements**
   - Collection reports for each crisis
   - Cleaning reports with statistics
   - Quality validation reports

### Statistical Robustness

1. **Sample Size Calculations**
   - Minimum 1,000 posts per crisis
   - Minimum 100 users per analysis
   - Power analysis for comparisons

2. **Multiple Comparison Corrections**
   - Bonferroni correction for multiple tests
   - False Discovery Rate (FDR) control
   - Significance level: p < 0.05

3. **Cross-Validation**
   - Bootstrap analysis (1,000 iterations)
   - Leave-one-out validation for network metrics
   - Temporal cross-validation (train on early, test on late)

---

## Ethical Considerations

### Privacy Protection

1. **Data Anonymization**
   - Pseudonymization of usernames in publications
   - No collection of private messages
   - No linking to external profiles

2. **Data Security**
   - Encrypted storage of raw data
   - Access control for sensitive data
   - Secure deletion after retention period

3. **Public Data Policy**
   - Only publicly accessible posts collected
   - Respect for deleted content
   - No circumvention of privacy settings

### Research Ethics

1. **Informed by IRB Principles**
   - Minimal harm principle
   - Public benefit justification
   - Respect for persons

2. **Transparency**
   - Open methodology
   - Reproducible analysis
   - Code and documentation publicly available

3. **Responsible Reporting**
   - Aggregate statistics preferred
   - No identification of individuals
   - Context-sensitive interpretation

### Platform Terms of Service

- Full compliance with Reddit API Terms
- Rate limiting respect
- Attribution where required
- No commercial use of data

---

## Analysis Pipeline

### Complete Workflow

```
1. Crisis Event Identification
   ↓
2. Configuration Setup (crisis_events.yaml)
   ↓
3. Data Collection (Reddit API)
   ↓
4. Data Cleaning (DataCleaner)
   ↓
5. Quality Validation (QualityValidator)
   ↓
6. Network Construction (CrisisNetworkAnalyzer)
   ↓
7. LIWC Analysis (LIWCCrisisAnalyzer)
   ↓
8. PADM Integration
   ↓
9. Statistical Analysis
   ↓
10. Results Interpretation
   ↓
11. Validation & Reporting
```

### Reproducibility Standards

1. **Version Control**
   - All code in Git repository
   - Tagged releases for publications
   - Configuration versioning

2. **Environment Management**
   - requirements.txt with pinned versions
   - Python version specification
   - Docker container (planned)

3. **Data Provenance**
   - Collection timestamps
   - API version used
   - Parameter documentation

4. **Analysis Documentation**
   - Parameter configurations saved
   - Random seeds documented
   - Analysis scripts versioned

---

## Validation Methods

### Internal Validation

1. **Data Quality Checks**
   - Automated quality validation
   - Manual spot-checking (5% sample)
   - Outlier investigation

2. **Network Validation**
   - Known community structure verification
   - Temporal consistency checks
   - Cross-layer consistency

3. **LIWC Validation**
   - Dictionary coverage analysis
   - Category correlation analysis
   - Baseline comparison

### External Validation

1. **News Media Comparison**
   - Timeline alignment with news reports
   - Event verification
   - Impact metric validation

2. **Cross-Platform Validation** (Planned)
   - Twitter data comparison
   - News API correlation
   - Academic dataset alignment

3. **Expert Review** (Planned)
   - Emergency management professional review
   - Crisis communication expert review
   - Domain expert validation

---

## Limitations and Future Work

### Current Limitations

1. **Single Platform**
   - Currently Reddit-only
   - Limited to English-language analysis
   - Platform-specific biases

2. **Temporal Constraints**
   - Historical data limitations
   - API access restrictions
   - Real-time analysis not implemented

3. **Analysis Scope**
   - LIWC dictionary limitations
   - Network scale constraints
   - Computational requirements

### Planned Improvements

1. **Multi-Platform Integration**
   - Twitter/X data collection
   - News API integration
   - Cross-platform network analysis

2. **Advanced Analytics**
   - Machine learning for classification
   - Predictive modeling
   - Real-time monitoring

3. **Visualization**
   - Interactive network visualizations
   - Temporal animation
   - Dashboard development

---

## References

### Key Methodological Papers

1. Lindell, M. K., & Perry, R. W. (2012). The Protective Action Decision Model (PADM). Journal of Emergency Management.

2. Wang, K., & Kogan, M. (2025). Resonance+ Metric for Crisis Communication. Social Computing Review.

3. Pennebaker, J. W., et al. (2015). Linguistic Inquiry and Word Count (LIWC2015).

### Network Analysis Foundation

1. Newman, M. E. J. (2018). Networks: An Introduction. Oxford University Press.

2. Barabási, A. L. (2016). Network Science. Cambridge University Press.

---

## Document Version

- **Version**: 1.0
- **Last Updated**: 2025-10-24
- **Maintainer**: Crisis Network Analysis Team

For questions or clarifications about methodology, please open an issue in the repository
