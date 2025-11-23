# GitHub Actions Workflows

This directory contains the CI/CD workflows for the dummyxarray project.

## Workflows Overview

### 1. CI Workflow (`ci.yml`)

**Triggers**: Push and PR to main/master/develop branches

**Jobs**:
- **Lint**: Code quality checks
  - Black formatting check
  - isort import sorting check
  - flake8 Python linting
  - markdownlint Markdown linting

- **Test**: Multi-platform and multi-version testing
  - Platforms: Ubuntu, macOS, Windows
  - Python versions: 3.9, 3.10, 3.11, 3.12
  - Uploads coverage to Codecov

- **Docs**: Documentation build verification
  - Builds MkDocs documentation
  - Uploads as artifact

### 2. Documentation Deployment (`docs.yml`)

**Triggers**: Push to main/master branch, manual dispatch

**Jobs**:
- Deploys documentation to GitHub Pages
- Uses MkDocs with Material theme
- Automatically updates on every main branch push

**Setup Required**:
1. Enable GitHub Pages in repository settings
2. Set source to "gh-pages" branch

### 3. Release Workflow (`release.yml`)

**Triggers**: Push tags matching `v*.*.*` (e.g., v0.1.0)

**Jobs**:
- **Test**: Runs full test suite before release
- **Release**: Creates GitHub release with changelog
- **PyPI**: Publishes package to PyPI

**Setup Required**:
1. Add `PYPI_TOKEN` secret to repository
   - Generate token at https://pypi.org/manage/account/token/
   - Add as repository secret

**Creating a Release**:
```bash
# Tag the release
git tag v0.1.0
git push origin v0.1.0

# Or use GitHub CLI
gh release create v0.1.0 --generate-notes
```

### 4. Dependency Updates (`dependencies.yml`)

**Triggers**: Weekly schedule (Monday 9 AM UTC), manual dispatch

**Jobs**:
- Updates pixi.lock with latest compatible versions
- Runs tests with updated dependencies
- Creates PR if updates are available

## Secrets Configuration

Required secrets for full CI/CD functionality:

| Secret | Purpose | How to Get |
|--------|---------|------------|
| `PYPI_TOKEN` | PyPI package publishing | https://pypi.org/manage/account/token/ |
| `CODECOV_TOKEN` | Code coverage reporting | https://codecov.io/ (optional) |

## Badge URLs

Update these in README.md with your repository information:

```markdown
[![CI](https://github.com/USERNAME/REPO/workflows/CI/badge.svg)](https://github.com/USERNAME/REPO/actions/workflows/ci.yml)
[![Documentation](https://img.shields.io/badge/docs-mkdocs-blue)](https://USERNAME.github.io/REPO/)
```

## Local Testing

Test workflows locally before pushing:

```bash
# Install act (GitHub Actions local runner)
brew install act  # macOS
# or download from https://github.com/nektos/act

# Run CI workflow locally
act -j lint
act -j test
```

## Workflow Maintenance

### Updating Python Versions

Edit the matrix in `ci.yml`:
```yaml
matrix:
  python-version: ['3.9', '3.10', '3.11', '3.12']
```

### Updating Platforms

Edit the matrix in `ci.yml`:
```yaml
matrix:
  os: [ubuntu-latest, macos-latest, windows-latest]
```

### Modifying Schedule

Edit the cron expression in `dependencies.yml`:
```yaml
schedule:
  - cron: '0 9 * * 1'  # Monday at 9 AM UTC
```

## Troubleshooting

### Workflow Not Triggering

1. Check branch protection rules
2. Verify workflow file syntax with `yamllint`
3. Check Actions tab for errors

### Failed Pixi Installation

1. Update `setup-pixi` action version
2. Check pixi.toml syntax
3. Verify platform compatibility

### Documentation Deployment Issues

1. Ensure GitHub Pages is enabled
2. Check gh-pages branch exists
3. Verify mkdocs.yml configuration

## Best Practices

1. **Always test locally** before pushing workflow changes
2. **Use matrix builds** for multi-platform/version testing
3. **Cache dependencies** to speed up workflows
4. **Fail fast** for quick feedback on errors
5. **Use secrets** for sensitive data, never hardcode
6. **Keep workflows DRY** using reusable workflows when possible

## Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Pixi Documentation](https://pixi.sh/)
- [MkDocs Documentation](https://www.mkdocs.org/)
- [PyPI Publishing Guide](https://packaging.python.org/guides/publishing-package-distribution-releases-using-github-actions-ci-cd-workflows/)
