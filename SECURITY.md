# Security Policy

## Intentional Vulnerabilities (Do NOT Report)

DVAI is **deliberately vulnerable**. The following are features, not bugs:

- Prompt injection in all forms
- System prompt leakage
- Insecure output handling (XSS, SQLi, command injection via LLM)
- Data extraction from models
- RAG poisoning and retrieval hijacking
- Agentic AI abuse (tool abuse, privilege escalation)
- Adversarial ML attacks
- Excessive agency exploits
- All challenge-related vulnerabilities

## Unintentional Vulnerabilities (Please Report)

If you find a vulnerability that is NOT part of a challenge, please report it:

- Arbitrary code execution on the host (outside of sandboxed challenges)
- Authentication bypass in the progress tracking system
- Path traversal that accesses real files outside the app
- Dependencies with known CVEs
- Container escape in Docker setup

## How to Report

Open a GitHub issue with:
1. Description of the vulnerability
2. Steps to reproduce
3. Whether it's exploitable in default configuration

Since DVAI is a local-only educational tool, there's no bounty program. But we'll credit you in the README.
