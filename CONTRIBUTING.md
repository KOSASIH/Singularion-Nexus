# Contributing to Singularion Nexus

We welcome contributions from the community! Here's how to get started.

## Getting Started

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Make your changes
4. Run tests: `pytest tests/ -v`
5. Commit: `git commit -m 'feat: add your feature'`
6. Push: `git push origin feature/your-feature`
7. Open a Pull Request

## Code Style

- Python: Follow PEP 8, use type hints
- Rust: Follow standard Rust formatting (`cargo fmt`)
- Commit messages: Use conventional commits (feat, fix, docs, etc.)

## Architecture Guidelines

- Keep modules loosely coupled
- Use async/await for all I/O operations
- Write unit tests for all new functionality
- Document public APIs with docstrings

## Security

- Never commit secrets or API keys
- Report security vulnerabilities privately
- All crypto implementations must be reviewed

## Code of Conduct

Be respectful, inclusive, and constructive.
