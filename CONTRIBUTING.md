# Contributing to Church Equipment Inventory System

Thank you for your interest in contributing to the Church Equipment Inventory System! This document provides guidelines and information for contributors.

## 🤝 How to Contribute

### Reporting Issues
- Use the GitHub issue tracker to report bugs or request features
- Include detailed information about the issue:
  - Steps to reproduce
  - Expected behavior
  - Actual behavior
  - Environment details (OS, Python version, etc.)
  - Screenshots if applicable

### Suggesting Features
- Open an issue with the "enhancement" label
- Describe the feature and its benefits
- Consider the impact on existing functionality
- Think about the user experience

### Code Contributions
1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/your-feature-name`
3. **Make your changes** following the coding standards below
4. **Test your changes** thoroughly
5. **Commit your changes**: `git commit -m 'Add feature: description'`
6. **Push to your fork**: `git push origin feature/your-feature-name`
7. **Create a Pull Request**

## 📋 Development Setup

### Prerequisites
- Python 3.11 or higher
- Git
- A code editor (VS Code, PyCharm, etc.)

### Local Development
1. Clone your fork:
   ```bash
   git clone https://github.com/yourusername/church-inventory-tracker.git
   cd church-inventory-tracker
   ```

2. Install dependencies:
   ```bash
   # Using uv (recommended)
   uv sync
   
   # Or using pip
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   ```bash
   export SESSION_SECRET="dev-secret-key"
   export FLASK_ENV=development
   export FLASK_DEBUG=1
   ```

4. Initialize the database:
   ```bash
   python -c "from app import app, db; app.app_context().push(); db.create_all()"
   ```

5. Run the development server:
   ```bash
   python app.py
   ```

## 🎯 Coding Standards

### Python Code Style
- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) style guidelines
- Use meaningful variable and function names
- Add docstrings to functions and classes
- Keep functions focused and concise
- Use type hints where appropriate

### Flask Best Practices
- Use Flask blueprints for organizing routes
- Implement proper error handling
- Use Flask-WTF for form validation
- Follow the application factory pattern
- Use environment variables for configuration

### Frontend Guidelines
- Use semantic HTML
- Follow Bootstrap 5 conventions
- Keep JavaScript modular and well-commented
- Ensure responsive design
- Test on multiple browsers

### Database Guidelines
- Use SQLAlchemy ORM for database operations
- Add proper indexes for performance
- Use migrations for schema changes
- Include data validation at the model level

## 🧪 Testing

### Running Tests
```bash
# Install test dependencies
pip install pytest pytest-flask

# Run tests
python -m pytest tests/
```

### Test Guidelines
- Write tests for new features
- Ensure good test coverage
- Use descriptive test names
- Test both success and failure cases
- Mock external dependencies

## 📝 Documentation

### Code Documentation
- Add docstrings to all functions and classes
- Use clear and concise language
- Include parameter descriptions
- Provide usage examples where helpful

### User Documentation
- Update README.md for new features
- Add screenshots for UI changes
- Include step-by-step instructions
- Keep documentation up to date

## 🔄 Pull Request Process

### Before Submitting
1. **Test thoroughly**: Ensure all functionality works as expected
2. **Check code style**: Run linting tools if available
3. **Update documentation**: Add or update relevant documentation
4. **Squash commits**: Clean up commit history if needed

### Pull Request Template
Use this template when creating a PR:

```markdown
## Description
Brief description of the changes made.

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Code refactoring
- [ ] Performance improvement

## Testing
- [ ] Tests pass locally
- [ ] Manual testing completed
- [ ] No breaking changes

## Screenshots (if applicable)
Add screenshots for UI changes.

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No new warnings
```

## 🏷️ Issue Labels

We use the following labels to categorize issues:
- `bug`: Something isn't working
- `enhancement`: New feature or request
- `documentation`: Improvements or additions to documentation
- `good first issue`: Good for newcomers
- `help wanted`: Extra attention is needed
- `question`: Further information is requested

## 📞 Getting Help

If you need help with contributing:
1. Check existing issues and pull requests
2. Join our community discussions
3. Contact the maintainers
4. Read the project documentation

## 🙏 Recognition

Contributors will be recognized in:
- The project README
- Release notes
- GitHub contributors page

Thank you for contributing to making church equipment management easier and more efficient! 