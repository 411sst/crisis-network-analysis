# API Reference

Complete API documentation for the Crisis Network Analysis project.

## Table of Contents

1. [Data Collection](#data-collection)
2. [Preprocessing](#preprocessing)
3. [Network Analysis](#network-analysis)
4. [LIWC Integration](#liwc-integration)
5. [Utilities](#utilities)

---

## Data Collection

### WorkingRedditCollector

The simplest and most reliable Reddit data collector.

#### Class: `WorkingRedditCollector`

```python
from src.collection.working_reddit_collector import WorkingRedditCollector

collector = WorkingRedditCollector(
    client_id='your_client_id',
    client_secret='your_client_secret',
    user_agent='Crisis Network Analysis v1.0'
)
```

#### Methods

##### `collect_posts(subreddit, limit=100, time_filter='week')`

Collect posts from a specific subreddit.

**Parameters:**
- `subreddit` (str): Name of the subreddit (without 'r/')
- `limit` (int): Maximum number of posts to collect (default: 100)
- `time_filter` (str): Time filter - 'hour', 'day', 'week', 'month', 'year', 'all' (default: 'week')

**Returns:**
- `pandas.DataFrame`: DataFrame containing collected posts

**Example:**
```python
df = collector.collect_posts('LosAngeles', limit=500, time_filter='week')
print(f"Collected {len(df)} posts")
```

##### `search_posts(subreddit, query, limit=100)`

Search for posts matching a query in a subreddit.

**Parameters:**
- `subreddit` (str): Name of the subreddit
- `query` (str): Search query string
- `limit` (int): Maximum number of posts (default: 100)

**Returns:**
- `pandas.DataFrame`: DataFrame containing search results

**Example:**
```python
df = collector.search_posts('California', query='wildfire', limit=200)
```

##### `save_to_csv(df, filename)`

Save DataFrame to CSV file.

**Parameters:**
- `df` (pandas.DataFrame): DataFrame to save
- `filename` (str): Output file path

**Example:**
```python
collector.save_to_csv(df, 'data/raw/la_wildfires.csv')
```

---

## Preprocessing

### DataCleaner

Comprehensive data cleaning for crisis social media data.

#### Class: `DataCleaner`

```python
from src.preprocessing.data_cleaner import DataCleaner

cleaner = DataCleaner(config={
    'remove_duplicates': True,
    'remove_deleted': True,
    'remove_bots': True,
    'min_content_length': 10,
    'max_content_length': 50000
})
```

#### Methods

##### `clean_dataset(df)`

Main cleaning pipeline for crisis data.

**Parameters:**
- `df` (pandas.DataFrame): Input DataFrame

**Returns:**
- `pandas.DataFrame`: Cleaned DataFrame

**Features:**
- Removes duplicates
- Cleans text content
- Handles missing values
- Removes deleted/removed content
- Filters bot accounts
- Validates content length
- Removes statistical outliers

**Example:**
```python
cleaned_df = cleaner.clean_dataset(raw_df)
print(f"Cleaned: {len(raw_df)} -> {len(cleaned_df)} rows")
```

##### `get_cleaning_report()`

Generate cleaning statistics report.

**Returns:**
- `dict`: Dictionary with cleaning statistics

**Example:**
```python
report = cleaner.get_cleaning_report()
print(f"Duplicates removed: {report['duplicates_removed']}")
print(f"Retention rate: {report['retention_rate']:.1f}%")
```

---

### QualityValidator

Validates data quality and provides quality metrics.

#### Class: `QualityValidator`

```python
from src.preprocessing.quality_validator import QualityValidator

validator = QualityValidator()
```

#### Methods

##### `validate_dataset(df, crisis_config=None)`

Comprehensive dataset validation.

**Parameters:**
- `df` (pandas.DataFrame): Input DataFrame
- `crisis_config` (dict, optional): Crisis configuration for relevance checking

**Returns:**
- `dict`: Dictionary with validation results including:
  - `completeness`: Column completeness metrics
  - `consistency`: Data consistency checks
  - `temporal_coverage`: Time coverage analysis
  - `content_quality`: Content quality metrics
  - `data_distribution`: Distribution analysis
  - `overall_score`: Overall quality score (0-100)

**Example:**
```python
results = validator.validate_dataset(df)
print(f"Overall quality score: {results['overall_score']:.2f}/100")
```

---

## Network Analysis

### CrisisNetworkAnalyzer

Comprehensive crisis network analysis framework.

#### Class: `CrisisNetworkAnalyzer`

```python
from src.networks.crisis_network_analyzer import CrisisNetworkAnalyzer

analyzer = CrisisNetworkAnalyzer('data/processed/master_dataset.csv')
```

#### Methods

##### `build_user_interaction_network()`

Build user-to-user interaction network.

**Returns:**
- `networkx.Graph`: User interaction network

**Example:**
```python
user_network = analyzer.build_user_interaction_network()
print(f"Nodes: {user_network.number_of_nodes()}")
print(f"Edges: {user_network.number_of_edges()}")
```

##### `build_multi_layer_networks()`

Build all network layers at once.

**Returns:**
- `dict`: Dictionary of network layers

**Example:**
```python
networks = analyzer.build_multi_layer_networks()
for name, network in networks.items():
    print(f"{name}: {network.number_of_nodes()} nodes")
```

---

## LIWC Integration

### LIWCCrisisAnalyzer

Enhanced LIWC analyzer for crisis network analysis with PADM integration.

#### Class: `LIWCCrisisAnalyzer`

```python
from src.liwc_integration import LIWCCrisisAnalyzer

liwc_analyzer = LIWCCrisisAnalyzer(network_analyzer=analyzer)
```

---

## Utilities

### ConfigLoader

Configuration management for the project.

#### Class: `ConfigLoader`

```python
from src.utils.config_loader import ConfigLoader

config = ConfigLoader(config_dir='config')
```

#### Methods

##### `load_crisis_events()`

Load crisis events configuration.

**Returns:**
- `dict`: Crisis events configuration

**Example:**
```python
crisis_config = config.load_crisis_events()
for crisis_id, details in crisis_config['crisis_events'].items():
    print(f"{crisis_id}: {details['name']}")
```

---

## Data Structures

### Post DataFrame Schema

Standard DataFrame schema for collected posts:

| Column | Type | Description |
|--------|------|-------------|
| `title` | str | Post title |
| `content` | str | Post content/text |
| `author` | str | Author username |
| `subreddit` | str | Subreddit name |
| `created_utc` | datetime | Post creation timestamp |
| `score` | int | Post score (upvotes - downvotes) |
| `num_comments` | int | Number of comments |
| `upvote_ratio` | float | Upvote ratio (0-1) |
| `url` | str | Post URL |
| `id` | str | Unique post ID |
| `permalink` | str | Reddit permalink |
| `crisis_id` | str | Crisis identifier (optional) |

---

## Version Information

- **API Version**: 1.0
- **Python Version**: 3.11+
- **Last Updated**: 2025-10-24

For issues or questions, please refer to the project repository
