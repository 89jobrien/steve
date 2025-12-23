---
description: Run parallel code review, test audit, and architecture analysis
author: Joseph OBrien
status: unpublished
updated: '2025-12-23'
version: 1.0.1
tag: commands
---

# Analyze Codebase

You MUST spawn the following three agents IN PARALLEL by making all Task tool calls in a SINGLE message. Do NOT wait for one to complete before starting the next.

## Parallel Analysis Tasks

Execute these simultaneously:

1. **Code Reviewer** (subagent_type: `code-reviewer`)
   - Review the codebase for quality, security vulnerabilities, and maintainability issues
   - Identify code smells, anti-patterns, and potential bugs
   - Check for OWASP top 10 vulnerabilities
   - Provide actionable feedback organized by priority (critical, high, medium, low)

2. **Test Engineer** (subagent_type: `test-engineer`)
   - Audit the existing test suite for coverage gaps
   - Evaluate test quality and effectiveness
   - Identify missing unit, integration, and e2e tests
   - Assess test organization and naming conventions
   - Check for flaky or brittle tests

3. **Architect Reviewer** (subagent_type: `architect-reviewer`)
   - Analyze the overall software architecture and codebase structure
   - Review for SOLID principles and proper layering
   - Identify opportunities for refactoring and optimization
   - Evaluate dependency management and module boundaries
   - Suggest architectural improvements for scalability and maintainability

4. **Performance Engineer** (subagent_type: `performance-engineer`)
   - Analyze the performance of the codebase
   - Identify performance bottlenecks
   - Evaluate performance metrics
   - Provide performance recommendations
   - Suggest performance improvements

5. **Security Engineer** (subagent_type: `security-engineer`)
   - Analyze the security of the codebase
   - Identify security vulnerabilities
   - Evaluate security metrics
   - Provide security recommendations
   - Suggest security improvements

6. **Logging Specialist** (subagent_type: `logging-specialist`)
   - Analyze the logging of the codebase
   - Identify logging issues
   - Evaluate logging metrics
   - Provide logging recommendations
   - Suggest logging improvements

## Output Requirements

After all agents complete, synthesize their findings into a unified report with:

- Executive summary of key findings
- Critical issues requiring immediate attention
- Recommended improvements prioritized by impact
- Quick wins vs long-term improvements
