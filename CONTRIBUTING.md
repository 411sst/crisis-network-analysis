# Contributing to Crisis Network Analysis

Thank you for your interest in contributing to the Crisis Network Analysis project! This document provides guidelines and instructions for contributing.

## Table of Contents

1. [Code of Conduct](#code-of-conduct)
2. [Getting Started](#getting-started)
3. [Development Setup](#development-setup)
4. [Making Changes](#making-changes)
5. [Testing](#testing)
6. [Code Style](#code-style)
7. [Commit Messages](#commit-messages)
8. [Pull Request Process](#pull-request-process)
9. [Project Structure](#project-structure)

---

## Code of Conduct

This project adheres to professional research ethics and open-source collaboration principles:

- Be respectful and inclusive
- Focus on constructive feedback
- Respect privacy and data protection
- Follow ethical research practices
- Acknowledge contributions appropriately

## Getting Started

### Prerequisites

- Python 3.11 or higher
- Git
- Basic understanding of network analysis and social computing
- Familiarity with pandas, networkx, and pytest

### Setting Up Your Environment

1. **Fork the repository**
   ```bash
   # Click "Fork" on GitHub, then clone your fork
   git clone https://github.com/YOUR_USERNAME/crisis-network-analysis.git
   cd crisis-network-analysis
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up API credentials** (for data collection)
   ```bash
   cp config/api_keys.env.template config/api_keys.env
   # Edit config/api_keys.env with your credentials
   ```

5. **Install pre-commit hooks** (optional but recommended)
   ```bash
   pip install pre-commit
   pre-commit install
   ```

6. **Run tests to verify setup**
   ```bash
   pytest tests/ -v
   ```

---

## Development Setup

### Creating a Development Branch

Always create a new branch for your work:

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/bug-description
```

Branch naming conventions:
- `feature/` - New features
- `fix/` - Bug fixes
- `docs/` - Documentation updates
- `refactor/` - Code refactoring
- `test/` - Test additions or modifications

---

## Making Changes

### What to Contribute

We welcome contributions in these areas:

1. **New Features**
   - Additional data collectors (Twitter, news APIs)
   - Advanced network analysis methods
   - Visualization tools
   - Machine learning models

2. **Bug Fixes**
   - Fix issues in existing code
   - Improve error handling
   - Performance optimizations

3. **Documentation**
   - API documentation improvements
   - Tutorial notebooks
   - Methodology clarifications
   - Code examples

4. **Tests**
   - Unit tests for new features
   - Integration tests
   - Edge case coverage

5. **Data Quality**
   - Improved preprocessing methods
   - Better validation techniques
   - Enhanced cleaning algorithms

### Areas That Need Help

Check the [Issues](https://github.com/411sst/crisis-network-analysis/issues) page for:
- Issues labeled `good first issue`
- Issues labeled `help wanted`
- Open feature requests

---

## Testing

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_preprocessing.py

# Run with coverage report
pytest --cov=src --cov-report=html

# Run only fast tests (skip slow integration tests)
pytest -m "not slow"
```

### Writing Tests

All new code should include tests:

1. **Unit Tests**: Test individual functions/methods
2. **Integration Tests**: Test component interactions
3. **Mock External APIs**: Use `unittest.mock` for API calls

Example test structure:
```python
import pytest
from src.preprocessing.data_cleaner import DataCleaner

class TestDataCleaner:
    @pytest.fixture
    def cleaner(self):
        return DataCleaner()

    def test_remove_duplicates(self, cleaner):
        # Test code here
        pass
```

### Test Coverage

- Aim for >80% code coverage
- All new features must have tests
- Critical functions should have 100% coverage

---

## Code Style

We follow Python best practices and PEP 8 with some modifications:

### Style Guidelines

- **Line length**: Max 100 characters
- **Indentation**: 4 spaces (no tabs)
- **Docstrings**: Google style
- **Type hints**: Use where appropriate

### Formatting Tools

```bash
# Format code with black
black src tests

# Sort imports with isort
isort src tests

# Lint with flake8
flake8 src tests
```

### Docstring Example

```python
def calculate_network_metrics(network: nx.Graph) -> Dict[str, float]:
    """
    Calculate basic network metrics.

    Args:
        network: NetworkX graph to analyze

    Returns:
        Dictionary containing metrics:
        - num_nodes: Number of nodes
        - num_edges: Number of edges
        - density: Network density

    Raises:
        ValueError: If network is empty

    Example:
        >>> G = nx.Graph()
        >>> G.add_edge('A', 'B')
        >>> metrics = calculate_network_metrics(G)
        >>> print(metrics['num_nodes'])
        2
    """
    if network.number_of_nodes() == 0:
        raise ValueError("Network cannot be empty")

    return {
        'num_nodes': network.number_of_nodes(),
        'num_edges': network.number_of_edges(),
        'density': nx.density(network)
    }
```

---

## Commit Messages

### Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `test`: Test additions/modifications
- `refactor`: Code refactoring
- `style`: Code style changes (formatting, etc.)
- `perf`: Performance improvements
- `chore`: Maintenance tasks

### Examples

```
feat(collection): add Twitter data collector

Implement Twitter API v2 integration for crisis data collection.
Includes rate limiting and error handling.

Closes #42
```

```
fix(preprocessing): handle missing timestamp values

Added null check for created_utc column before datetime conversion.
Prevents crashes when processing incomplete data.

Fixes #89
```

---

## Pull Request Process

### Before Submitting

1. **Update your branch**
   ```bash
   git fetch origin
   git rebase origin/main
   ```

2. **Run all tests**
   ```bash
   pytest tests/ -v
   ```

3. **Format your code**
   ```bash
   black src tests
   isort src tests
   flake8 src tests
   ```

4. **Update documentation**
   - Update docstrings
   - Update API reference if needed
   - Add examples if appropriate

### Submitting a PR

1. **Push your branch**
   ```bash
   git push origin feature/your-feature-name
   ```

2. **Create Pull Request on GitHub**
   - Use a descriptive title
   - Fill out the PR template
   - Link related issues
   - Add screenshots if UI changes

3. **PR Template Checklist**
   - [ ] Tests pass locally
   - [ ] Code follows style guidelines
   - [ ] Documentation updated
   - [ ] No merge conflicts
   - [ ] Changelog updated (for significant changes)

### Review Process

1. Automated CI/CD checks will run
2. Maintainers will review your code
3. Address any requested changes
4. Once approved, your PR will be merged

### After Merging

1. Delete your feature branch
2. Pull the latest main branch
3. Start a new branch for your next contribution

---

## Project Structure

Understanding the project layout:

```
crisis-network-analysis/
├── src/                    # Source code
│   ├── collection/         # Data collectors
│   ├── preprocessing/      # Data cleaning and validation
│   ├── networks/          # Network analysis
│   ├── social_computing/  # PADM and LIWC integration
│   ├── visualization/     # Visualization tools
│   └── utils/             # Utilities (config, logging)
├── tests/                 # Test files
├── config/                # Configuration files
├── data/                  # Data directory (gitignored)
├── results/               # Analysis results
├── notebooks/             # Jupyter notebooks
├── docs/                  # Documentation
└── scripts/               # Utility scripts
```

### Key Files

- `requirements.txt` - Python dependencies
- `pytest.ini` - Test configuration
- `.gitignore` - Git ignore rules
- `README.md` - Project overview
- `CONTRIBUTING.md` - This file!

---

## Questions?

- Check the [Documentation](docs/)
- Search [Issues](https://github.com/411sst/crisis-network-analysis/issues)
- Ask in [Discussions](https://github.com/411sst/crisis-network-analysis/discussions)

---

## Recognition

Contributors will be acknowledged in:
- README.md contributors section
- Release notes
- Academic publications (for significant contributions)

Thank you for contributing to crisis communication research!
