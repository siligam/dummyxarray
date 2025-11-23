# Contributing to dummyxarray

Thank you for your interest in contributing to dummyxarray! This document provides guidelines and instructions for contributing.

## Development Setup

### Prerequisites

- [Pixi](https://pixi.sh/) package manager
- Git

### Getting Started

1. Fork the repository on GitHub
2. Clone your fork:
   ```bash
   git clone https://github.com/YOUR_USERNAME/fakexarray.git
   cd fakexarray
   ```

3. Install dependencies with pixi:
   ```bash
   pixi install
   ```

4. Create a new branch for your feature:
   ```bash
   git checkout -b feature/your-feature-name
   ```

## Development Workflow

### Running Tests

```bash
# Run all tests
pixi run test

# Run specific test
pixi run test -k test_name
```

### Code Quality

Before submitting a PR, ensure your code passes all quality checks:

```bash
# Format code
pixi run format

# Check formatting
pixi run check-format

# Run linters
pixi run lint

# Run all checks
pixi run check
```

### Documentation

If you're adding new features, please update the documentation:

```bash
# Serve documentation locally
pixi run docs-serve

# Build documentation
pixi run docs-build
```

## Coding Standards

### Python Code

- **Line length**: Maximum 100 characters
- **Formatting**: Use `black` (configured in `pyproject.toml`)
- **Import sorting**: Use `isort` with black profile
- **Linting**: Code must pass `flake8` checks

### Docstrings

Use NumPy-style docstrings:

```python
def example_function(param1, param2):
    """
    Brief description of the function.
    
    Longer description if needed.
    
    Parameters
    ----------
    param1 : type
        Description of param1
    param2 : type
        Description of param2
        
    Returns
    -------
    type
        Description of return value
        
    Examples
    --------
    >>> example_function(1, 2)
    3
    """
    return param1 + param2
```

### Commit Messages

Follow conventional commit format:

- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation changes
- `style:` - Code style changes (formatting, etc.)
- `refactor:` - Code refactoring
- `test:` - Adding or updating tests
- `chore:` - Maintenance tasks

Example:
```
feat: add assign_attrs method for xarray compatibility

- Implement assign_attrs for DummyDataset and DummyArray
- Add tests for method chaining
- Update documentation with examples
```

## Pull Request Process

1. **Update tests**: Add tests for new features or bug fixes
2. **Update documentation**: Update README.md and docs/ as needed
3. **Run quality checks**: Ensure `pixi run check` passes
4. **Update CHANGELOG**: Add entry describing your changes
5. **Submit PR**: Create a pull request with a clear description

### PR Checklist

- [ ] Tests pass (`pixi run test`)
- [ ] Code is formatted (`pixi run format`)
- [ ] Linting passes (`pixi run lint`)
- [ ] Documentation is updated
- [ ] CHANGELOG is updated
- [ ] Commit messages follow conventions

## Testing Guidelines

### Writing Tests

- Place tests in `tests/` directory
- Use descriptive test names: `test_<feature>_<scenario>`
- Group related tests in classes
- Use pytest fixtures for common setup

Example:
```python
def test_assign_attrs_basic():
    """Test basic attribute assignment."""
    ds = DummyDataset()
    ds.assign_attrs(title="Test")
    assert ds.attrs["title"] == "Test"

def test_assign_attrs_chaining():
    """Test method chaining with assign_attrs."""
    ds = DummyDataset()
    result = ds.assign_attrs(a=1).assign_attrs(b=2)
    assert result is ds
    assert ds.attrs == {"a": 1, "b": 2}
```

## Reporting Issues

When reporting issues, please include:

- **Description**: Clear description of the issue
- **Steps to reproduce**: Minimal code example
- **Expected behavior**: What you expected to happen
- **Actual behavior**: What actually happened
- **Environment**: Python version, OS, package versions

## Questions?

Feel free to open an issue for questions or discussions about:

- Feature requests
- Design decisions
- Implementation details
- Documentation improvements

## Code of Conduct

- Be respectful and inclusive
- Focus on constructive feedback
- Help others learn and grow
- Assume good intentions

Thank you for contributing! 🎉
