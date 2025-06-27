# SECURITY of FastAPI-fastkit

For users new to Python and FastAPI, keeping the FastAPI-fastkit open source healthy is one of the critical challenges.

To maintain the security and stability of FastAPI-fastkit for users new to Python and FastAPI & FastAPI-fastkit contributors, please follow these guidelines.

## Template Project Security Requirements

1. All template projects must meet these security requirements:
   - Sensitive information management through environment variables (.env)
   - Basic authentication/authorization system implementation
   - CORS configuration implementation
   - Proper exception handling and logging system

2. Dependency Management:
   - No use of packages with known security vulnerabilities
   - Version specification required in requirements.txt
   - Use of versions with latest security patches

## Vulnerability Reporting

If you discover a security vulnerability:
1. Report via GitHub Issues
2. Contact project maintainer directly (bbbong9@gmail.com)
3. Keep vulnerability private until resolved

## Security Checks

All template projects must pass these automated security checks:

### Required Checks
- Template validation through inspector.py
- Code quality and security static analysis
- Dependency vulnerability scanning through GitHub Actions

## Security Best Practices for Contributors

### Template Development
1. **Environment Variables**: Always use `.env` files for sensitive data
2. **Authentication**: Implement proper authentication mechanisms
3. **Input Validation**: Validate all user inputs
4. **Error Handling**: Don't expose sensitive information in error messages
5. **Dependencies**: Keep dependencies minimal and up-to-date

### Code Security
1. **No hardcoded secrets**: Use environment variables
2. **SQL Injection Prevention**: Use parameterized queries
3. **XSS Prevention**: Properly sanitize outputs
4. **CSRF Protection**: Implement CSRF tokens where needed

### Development Practices
```bash
# Before committing changes
make dev-check  # Runs code checks

# Regular dependency updates
pip list --outdated
make clean && make dev-setup  # Refresh environment
```

## Template Security Checklist

Before submitting a new template, ensure:

- [ ] All sensitive data uses environment variables
- [ ] Authentication/authorization implemented
- [ ] CORS properly configured
- [ ] Input validation in place
- [ ] Error handling doesn't expose sensitive data
- [ ] Dependencies are up-to-date and secure
- [ ] `make dev-check` passes all tests
- [ ] No hardcoded secrets or credentials
- [ ] SQL queries use parameterization
- [ ] Proper logging configuration

## Automated Security Monitoring

This project uses:
- **GitHub Dependabot**: Automatic dependency updates
- **GitHub Actions**: Security scanning on PRs
- **Code scanning**: Static analysis for vulnerabilities (will be added soon)

## Security Updates

All security updates are documented in:
- [GitHub Releases](https://github.com/bnbong/FastAPI-fastkit/releases)
- [Changelog](https://bnbong.github.io/FastAPI-fastkit/changelog/)

## Discussion

For security-related discussions, please use:
- GitHub Security Advisories (for vulnerabilities)
- GitHub Discussions - Security category (for general security topics)
- Direct email contact for sensitive matters

---
@author bnbong bbbong9@gmail.com
