# Security Policy

## Supported Versions

We take security seriously in the Leo project. The following versions are currently supported with security updates:

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |

## Reporting a Vulnerability

If you discover a security vulnerability within Leo, please report it responsibly by following these steps:

### Private Disclosure

1. **DO NOT** create a public GitHub issue for security vulnerabilities
2. Send an email to: `tuanleducanh78202(at)gmail.com`
3. Include the following information:
   - Description of the vulnerability
   - Steps to reproduce the issue
   - Potential impact assessment
   - Suggested fix (if you have one)

### What to Expect

- **Acknowledgment**: We will acknowledge receipt of your vulnerability report within 48 hours
- **Assessment**: We will assess the vulnerability and provide an initial response within 5 business days
- **Updates**: We will keep you informed of our progress throughout the investigation
- **Resolution**: We aim to resolve critical vulnerabilities within 30 days
- **Credit**: We will credit you in our security advisory (unless you prefer to remain anonymous)

## Security Considerations

### Infrastructure Security

- **Database Security**: MongoDB instances should be properly secured with authentication and network isolation
- **API Security**: FastAPI endpoints should implement proper authentication and rate limiting
- **Container Security**: Docker containers should run with minimal privileges and be regularly updated
- **Environment Variables**: Sensitive configuration should be stored securely using environment variables

### Data Protection

- **API Keys**: All API keys (OpenAI, Google GenAI, AWS, etc.) must be stored securely and rotated regularly
- **Data Encryption**: Sensitive data should be encrypted at rest and in transit
- **Access Control**: Implement proper access controls for data and system resources
- **Data Retention**: Follow data retention policies and securely delete data when no longer needed

### Model Security

- **Model Integrity**: Ensure ML models are obtained from trusted sources and verify checksums
- **Input Validation**: Validate all inputs to prevent injection attacks
- **Output Sanitization**: Sanitize model outputs to prevent potential exploits
- **Resource Limits**: Implement resource limits to prevent resource exhaustion attacks

### Web Application Security

- **CORS Configuration**: Properly configure CORS settings for the frontend
- **Input Validation**: Validate all user inputs on both client and server side
- **Authentication**: Implement secure authentication mechanisms
- **HTTPS**: Always use HTTPS in production environments
- **CSP Headers**: Implement Content Security Policy headers

## Best Practices

### For Developers

1. **Dependencies**: Regularly update dependencies and monitor for known vulnerabilities
2. **Code Review**: All code should be reviewed before merging
3. **Secret Management**: Never commit secrets to version control
4. **Least Privilege**: Run services with minimal required permissions
5. **Logging**: Implement proper logging without exposing sensitive information

### For Deployment

1. **Network Security**: Use firewalls and network segmentation
2. **Monitoring**: Implement security monitoring and alerting
3. **Backup**: Maintain secure backups of critical data
4. **Updates**: Keep all systems and dependencies updated
5. **Access Control**: Implement proper access controls and regular access reviews

## Security Tools and Configurations

### Pre-commit Hooks

This project uses pre-commit hooks to catch security issues early:

- Code linting with Ruff
- Security scanning for common vulnerabilities
- Secrets detection

### Dependency Management

- Use `uv` for Python dependency management
- Regular dependency updates via dependabot or similar tools
- Vulnerability scanning of dependencies

### Container Security

- Use minimal base images
- Run containers as non-root users
- Regularly update container images
- Scan images for vulnerabilities

## Incident Response

In case of a security incident:

1. **Immediate Response**: Isolate affected systems to prevent further damage
2. **Assessment**: Assess the scope and impact of the incident
3. **Communication**: Notify relevant stakeholders and users if necessary
4. **Recovery**: Implement fixes and restore normal operations
5. **Post-Incident**: Conduct a post-incident review and update security measures

## Security Resources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework)
- [Python Security Best Practices](https://python.org/dev/security/)
- [Docker Security Best Practices](https://docs.docker.com/engine/security/)

## Compliance

This project aims to follow security best practices and may need to comply with:

- Data protection regulations (GDPR, CCPA, etc.)
- Industry-specific security standards
- Organizational security policies

## Contact

For security-related questions or concerns:

- Email: tuanleducanh78202(at)gmail.com
- Please review our [Code of Conduct](CODE_OF_CONDUCT.md) for community guidelines

## Changelog

### Version 0.1.0

- Initial security policy established
- Basic security guidelines implemented
- Vulnerability reporting process defined

---

**Note**: This security policy is a living document and will be updated as the project evolves and new security considerations arise.
