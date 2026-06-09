# Contributing to TokenSage-CLI

Thank you for your interest in contributing to TokenSage-CLI!

## Development Setup

1. Clone the repository
2. Ensure Python 3.8+ is installed
3. No external dependencies required (rich is optional)

```bash
# Install in development mode
pip install -e .

# Install with optional rich support
pip install -e ".[rich]"

# Run tests
python -m pytest tests/

# Run a specific test
python -m pytest tests/test_token_counter.py -v
```

## Code Style

- All code comments in English
- All docstrings in English
- Follow PEP 8 conventions
- Zero external dependencies (rich is optional enhancement)

## Project Structure

```
tokensage-cli/
├── tokensage/          # Main package
│   ├── models/         # Data models
│   ├── token_counter.py
│   ├── compressor.py
│   ├── cost_calculator.py
│   ├── cn_optimizer.py
│   ├── tui_dashboard.py
│   ├── proxy_mode.py
│   ├── config_manager.py
│   └── cli.py
├── tests/              # Unit tests
└── setup.py
```

## Pull Request Process

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Ensure all tests pass
5. Submit a pull request

## Reporting Issues

Please use GitHub Issues to report bugs or request features.
