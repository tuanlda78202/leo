# Contributing Guidelines

Thank you for your interest in contributing to Leo! 🎉

We welcome all kinds of contributions - from bug reports and feature requests to code improvements and documentation updates. This guide will help you get started.

Please note that this project is released with a [Contributor Code of Conduct](CODE_OF_CONDUCT.md). By participating in this project you agree to abide by its terms.

## 📋 Table of Contents

- [How to Contribute](#how-to-contribute)
- [Development Workflow](#development-workflow)
- [Code Standards](#code-standards)
- [Testing](#testing)
- [Pull Request Process](#pull-request-process)
- [Issue Guidelines](#issue-guidelines)
- [Community](#community)

## How to Contribute

There are many ways to contribute to Leo:

### 🐛 Report Bugs

- Use our [bug report template](.github/ISSUE_TEMPLATE/bug_report.yaml)
- Check existing issues first to avoid duplicates
- Provide detailed reproduction steps and environment information

### 💡 Suggest Features

- Use our [feature request template](.github/ISSUE_TEMPLATE/feature_request.yaml)
- Explain the use case and expected behavior
- Consider the scope and feasibility of the feature

### 📝 Improve Documentation

- Fix typos or clarify existing documentation
- Add examples or tutorials
- Improve code comments and docstrings

### 🔧 Submit Code Changes

- Fix bugs or implement new features
- Improve performance or code quality
- Add or improve tests

### 💬 Help Others

- Answer questions in issues and discussions
- Review pull requests
- Share your Leo experience with the community

## Development Workflow

### 1. Create a Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/your-bug-fix
```

### 2. Make Changes

- Write code following our [code standards](#code-standards)
- Add tests for new functionality
- Update documentation as needed

### 3. Test Your Changes

```bash
make check
```

### 4. Commit Your Changes

We follow [Conventional Commits](https://www.conventionalcommits.org/):

```bash
git commit -m "feat: add new RAG retrieval method"
git commit -m "fix: resolve MongoDB connection timeout"
git commit -m "docs: update API documentation"
```

### 5. Push and Create PR

```bash
git push origin your-branch-name
```

Then create a pull request using our [PR template](.github/PULL_REQUEST_TEMPLATE.md).

## Code Standards

### Python Code Style

- **Formatter**: [Ruff](https://docs.astral.sh/ruff/) for code formatting
- **Linter**: Ruff for code linting and import sorting
- **Type Hints**: Use type hints for all function parameters and return values
- **Docstrings**: Use Google-style docstrings for functions and classes

### TypeScript/React Code Style

- **ESLint**: For code linting
- **Prettier**: For code formatting (via package.json config)
- **TypeScript**: Strict mode enabled

### General Guidelines

- **Line Length**: Maximum 88 characters for Python, 100 for TypeScript
- **Imports**: Sort imports alphabetically and group them properly
- **Variables**: Use descriptive names, avoid abbreviations
- **Comments**: Write clear, concise comments explaining "why", not "what"

### Code Quality Tools

```bash
# Format code
make format-fix

# Fix linting issues
make lint-fix

# Check everything
make ci
```

## Testing

### Running Tests

```bash
# BE tests
cd app/offline_sys && uv run pytest
cd app/online_sys && uv run pytest

# FE tests
cd app/online_sys/ui && npm test
```

### Writing Tests

- Write unit tests for new functions and classes
- Add integration tests for API endpoints
- Include edge cases and error scenarios
- Aim for good test coverage, but focus on quality over quantity

### Test Structure

```python
def test_function_name():
    # Arrange
    input_data = {...}

    # Act
    result = function_under_test(input_data)

    # Assert
    assert result == expected_result
```

## Pull Request Process

### Before Submitting

- [ ] Code follows our style guidelines
- [ ] All tests pass locally
- [ ] Pre-commit hooks pass
- [ ] Documentation is updated (if applicable)
- [ ] Commit messages follow conventional format

### PR Requirements

1. **Title**: Clear, descriptive title following conventional commits
2. **Description**: Use our PR template to provide context
3. **Size**: Keep PRs focused and reasonably sized
4. **Tests**: Include tests for new functionality
5. **Documentation**: Update docs for user-facing changes

### Review Process

1. **Automated Checks**: CI must pass (format, lint, tests)
2. **Code Review**: At least one maintainer review required
3. **Testing**: Manual testing for significant changes
4. **Approval**: Maintainer approval before merge

### After Approval

- PRs are typically merged using "Squash and Merge"
- Delete your feature branch after merging
- Update your local main branch

## Issue Guidelines

### Before Creating an Issue

- Search existing issues to avoid duplicates
- Check if it's already fixed in the latest version
- Gather relevant information (logs, screenshots, etc.)

### Issue Types

- **Bug Report**: Something is broken or not working as expected
- **Feature Request**: New functionality or enhancement
- **Question**: Need help or clarification
- **Documentation**: Improvements to docs

### Writing Good Issues

- **Clear Title**: Summarize the issue in one line
- **Detailed Description**: Explain the problem or request
- **Steps to Reproduce**: For bugs, provide clear reproduction steps
- **Environment**: Include relevant system information
- **Expected vs Actual**: What should happen vs what actually happens

## Community

### Getting Help

- **GitHub Issues**: For bugs and feature requests
- **GitHub Discussions**: For questions and general discussion
- **Email**: tuanleducanh78202(at)gmail.com for private matters

### Communication Guidelines

- Be respectful and inclusive
- Stay on topic and be constructive
- Help others when you can
- Follow our [Code of Conduct](CODE_OF_CONDUCT.md)

## 🔒 Security

For security-related issues, please review our [Security Policy](SECURITY.md) and report vulnerabilities responsibly.

## 📄 License

By contributing to Leo, you agree that your contributions will be licensed under the same [MIT License](LICENSE) that covers the project.

---

## 🙏 Thank You

Your contributions make Leo better for everyone. Whether you're fixing a typo, adding a feature, or helping other users, every contribution is valuable and appreciated!

For questions about contributing, feel free to reach out through GitHub issues or discussions.
