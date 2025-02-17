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
- Template validation through inspector.py
- Code quality and security static analysis
- Dependency vulnerability scanning through GitHub Actions (this is done by Github Actions during the new package version deployment phase for the entire project template.)

## Discussion

For security-related discussions, please use the Security category in GitHub Discussions.

---
@author bnbong bbbong9@gmail.com
