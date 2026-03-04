---
status: DEPRECATED
deprecated_in: "2026-01-20"
name: requirements-elicitation
description: Systematic workflow for extracting complete, unambiguous specifications from incomplete or ambiguous inputs. Orchestrates question-driven elicitation, multi-stakeholder analysis, and systematic completeness verification. Use when gathering requirements, reviewing specs, or when facing unclear stakeholder intent.
user-invocable: true
allowed-tools: clarifying-questions, specification-elicitation, stakeholder-analysis, information-completeness, conceptual-analysis, framing-skepticism, deliverable-completeness, documentation-quality, evidence-reasoning
---


# Requirements Elicitation

## Core Principle

**The quality of requirements is determined by the quality of questions asked, viewed through multiple
stakeholder lenses, and verified across all dimensions of completeness.** This workflow transforms
incomplete descriptions into actionable, comprehensive specifications.

## When to Use This Workflow

-   Receiving brief notes or incomplete descriptions
-   Gathering requirements for new features or systems
-   Reviewing existing specifications for completeness
-   Requirements have gaps between stated need and actionable specification
-   Unclear stakeholder intent or missing cross-functional requirements
-   Temptation to "fill in" gaps with assumptions
-   Before starting implementation of any significant feature

## Workflow Overview

This workflow orchestrates these atomic skills:

-   `pre-task-checkpoint` - Problem framing and analysis before elicitation
-   `clarifying-questions` - Reactive response to ambiguity
-   `specification-elicitation` - Proactive 5-level question framework
-   `stakeholder-analysis` - Multi-perspective analysis (8 stakeholder types)
-   `information-completeness` - 9-dimension information gathering
-   `conceptual-analysis` - Understanding true intent beyond literal statements
-   `framing-skepticism` - Challenging embedded assumptions
-   `deliverable-completeness` - 6-dimension specification verification
-   `documentation-quality` - Ensuring specifications add value
-   `evidence-reasoning` - Evidence-based validation

## Progressive Depth Paths

This workflow supports three depth levels based on complexity and stakes:

### Quick Path (Simple Features, Low Risk)

```
Entry → Phase 1 → Phase 2 (L1-L2) → Phase 3 (Quick stakeholder check) →
Phase 4 (Dimensions 1-3) → Phase 5 (Exit)
```

**Use when:**

-   Single-stakeholder feature (e.g., internal tool)
-   Well-understood domain
-   Low operational complexity
-   Minimal cross-system integration

**Time:** 30-60 minutes

### Standard Path (Most Features)

```
Entry → Phase 1 → Phase 2 (L1-L4) → Phase 3 (Core stakeholders) →
Phase 4 (All 6 dimensions) → Phase 5 (Quality checks) → Phase 6 (Exit)
```

**Use when:**

-   Multi-stakeholder impact
-   Moderate complexity
-   Some integration concerns
-   Standard operational requirements

**Time:** 2-4 hours

### Comprehensive Path (Complex/High-Stakes)

```
Entry → Phase 1 → Phase 2 (L1-L5) → Phase 3 (All 8 stakeholders) →
Phase 4 (All 6 dimensions) → Phase 4.5 (Information completeness 9D) →
Phase 5 (Quality gates) → Phase 6 (Evidence validation) → Phase 7 (Exit)
```

**Use when:**

-   Mission-critical features
-   High operational risk
-   Complex multi-system integration
-   Regulatory/compliance requirements
-   Novel or experimental features

**Time:** 1-2 days

## Phase 1: Entry Point & Problem Framing

**Invoke: `pre-task-checkpoint`**

Before starting elicitation, establish foundation:

```
□ Checkpoint 1: Problem Framing
  - What PROBLEM does this feature solve? (not "what feature to build")
  - Is the request a solution masquerading as a requirement?
  - Can the underlying need be addressed differently?
  - What business outcome is the stakeholder trying to achieve?

□ Checkpoint 2: Familiarity Check
  - Have I implemented similar features before? → RED FLAG
  - Familiar domain = higher risk of assumption-driven gaps
  - Similar ≠ same (different context = different requirements)

□ Checkpoint 3: Framework Selection
  - Complexity level? → Choose depth path
  - Which atomic skills will this workflow need?

□ Checkpoint 4: Initial Scope Assessment
  - Is this a new feature, enhancement, or system?
  - What's explicitly stated vs implicitly assumed?
  - Who are the likely affected stakeholders?

□ Checkpoint 5: Resource Allocation
  - PARSIMONY: What's the simplest elicitation approach?
  - SCOPE: Are we gathering actual needs or hypothetical ones?
  - INFORMATION ECONOMY: What existing documentation exists?
```

**Invoke: `framing-skepticism`**

Challenge the task framing:

```
□ How has the stakeholder framed this request?
  - Is it framed as a solution? ("Add feature X")
  - Or as a problem? ("Users can't accomplish Y")

□ Separate observation from interpretation:
  - Observation: What's the stated request?
  - Interpretation 1: Accept framing as-is
  - Interpretation 2: Question underlying assumption
  - Root cause: What's the actual need?

□ Question embedded constraints:
  - What constraints are implicit in the framing?
  - Must solution follow suggested approach?
  - Are there alternative framings to explore?
```

**Exit Criteria:** Problem framing established, depth path selected, assumptions surfaced

## Phase 2: Question-Driven Elicitation

**Invoke: `specification-elicitation`**

Apply 5-level question framework systematically. Depth depends on path selected.

### Level 1: Surface Clarification (ALL PATHS)

_Addresses obvious gaps in stated requirements_

```
Questions to generate:
✅ What are the explicit inputs/outputs?
✅ What file types/formats/sizes are involved?
✅ What are the basic acceptance criteria?
✅ What does success look like?
✅ What are the core user actions?

Anti-patterns:
❌ Assuming "reasonable defaults" without validation
❌ Filling gaps with "industry standard" practices
❌ Moving forward with open questions
```

### Level 2: Edge Case Exploration (QUICK+ PATHS)

_Probes boundaries and failure modes_

```
Questions to generate:
✅ What happens if operation fails? Retry policy?
✅ What if user input is invalid/malicious?
✅ What if external dependencies are unavailable?
✅ What are the rate limits/quotas?
✅ What if operation takes too long? Timeout? User cancellation?
✅ What if it's the FIRST time? LAST time? ONLY one?

Edge case discovery framework:
- What if it's ALREADY done? (idempotency)
- What if it's CONCURRENT? (race conditions)
- What if it FAILS HALFWAY? (partial state, recovery)
- What if there are MANY? (performance, pagination)
```

### Level 3: Constraint Discovery (STANDARD+ PATHS)

_Surfaces hidden requirements and quantified targets_

```
Questions to generate:
✅ What are the performance requirements?
  - Latency: p50, p95, p99 targets?
  - Throughput: requests/sec, data volume?
  - Concurrent users: expected scale?

✅ What are the data requirements?
  - Volume: how much data?
  - Growth: expected growth rate?
  - Retention: how long to keep?

✅ What are the availability requirements?
  - Uptime SLA?
  - Acceptable downtime window?
  - Disaster recovery: RPO, RTO?

✅ What are the security requirements?
  - Data sensitivity classification?
  - Compliance needs (GDPR, HIPAA, etc.)?
  - Encryption requirements?
```

### Level 4: Cross-Cutting Concerns (STANDARD+ PATHS)

_Systematic gap checking across operational dimensions_

```
Questions to generate by category:

AUTHENTICATION & AUTHORIZATION:
✅ Who can access this feature?
✅ What's the permission model?
✅ Session management approach?
✅ API authentication mechanism?

ERROR HANDLING:
✅ What error categories exist?
✅ User-facing vs system error messages?
✅ Retry/recovery strategies?
✅ Error logging requirements?

MONITORING & DEBUGGING:
✅ What metrics should we track?
✅ What alerts should fire?
✅ What logging is needed for debugging?
✅ Distributed tracing requirements?

AUDIT & COMPLIANCE:
✅ What actions need audit logs?
✅ What data retention policies apply?
✅ What regulatory requirements exist?
```

### Level 5: Stakeholder Perspective Shift (COMPREHENSIVE PATH)

_Multi-role analysis to uncover role-specific requirements_

```
For each affected stakeholder type:
✅ From Ops perspective: What are monitoring/scaling/reliability needs?
✅ From Security perspective: What's the threat model?
✅ From Support perspective: What are debugging/troubleshooting needs?
✅ From QA perspective: How is this testable? What are test scenarios?
✅ From Analytics perspective: What events should we track?
✅ From Developer perspective: What integration points exist?
```

**Question Formulation Best Practices:**

```
1. Offer Multiple Options
   ✅ "Handle duplicates by: (a) rejecting, (b) merging, (c) allowing with warning?"
   ❌ "How should we handle duplicates?" (too open-ended)

2. Provide Context
   ✅ "For error handling: retry automatically (better UX, might duplicate)
       or require user retry (safer but more friction)?"
   ❌ "Should we retry on errors?" (unclear implications)

3. Surface Trade-offs
   ✅ "Optimize for speed (cache aggressively, eventual consistency) or
       correctness (always fresh, slight latency)?"
   ❌ "Should this be fast?" (ignores trade-off)

4. Ask About Absence
   ✅ "No mention of bulk operations - intentional (YAGNI) or oversight?"
   ❌ Just assume not needed

5. Probe Consequences
   ✅ "Unlimited file size requires chunking, resumable uploads, storage
       quotas. Is this in scope?"
   ❌ Accept "unlimited" without exploring implications
```

**Invoke: `clarifying-questions`**

For any ambiguous responses, immediately ask clarifying questions:

```
Essential dimensions to clarify:
| Dimension | Question |
|-----------|----------|
| **Goal/Context** | What is the primary goal? What's the context? |
| **Scope** | Simple fix or comprehensive solution? |
| **Success Criteria** | What defines success? How measured? |
| **Constraints** | What constraints exist? (time, dependencies) |
| **Depth** | Quick feedback or thorough implementation? |

Make assumptions explicit:
❌ ASSUMPTION: "File size limit probably 5MB"
✅ VALIDATION: "I'll assume 5MB limit unless you specify otherwise"
```

**Exit Criteria:** All relevant question levels completed, stakeholder responses documented, assumptions
validated

## Phase 3: Multi-Stakeholder Analysis

**Invoke: `stakeholder-analysis`**

Analyze requirements from all affected stakeholder perspectives. Scope depends on path.

### Quick Path: Core Stakeholders Only

```
□ Product Owner / Business
□ End User
□ Developer (Implementer)
```

### Standard Path: Extended Stakeholder Set

```
□ Product Owner / Business
□ End User
□ Developer (Implementer)
□ QA / Testing
□ Operations / SRE
□ Security (if applicable)
```

### Comprehensive Path: Full Stakeholder Matrix

```
□ Product Owner / Business
□ End User
□ Developer (Implementer)
□ QA / Testing
□ Operations / SRE
□ Security
□ Support / Customer Success
□ Data / Analytics
```

### Stakeholder Analysis Process

**For each stakeholder:**

```
1. IDENTIFY concerns:
   - What are your concerns about this feature?
   - What would make this a success for you?
   - What would make this a failure?
   - What's missing from current description?
   - What risks do you see?

2. EXTRACT requirements:
   - Product Owner → Business metrics, ROI, success criteria
   - End User → Usability, error recovery, accessibility
   - Developer → Technical feasibility, integration points
   - QA → Testability, acceptance criteria, test scenarios
   - Ops → Monitoring, alerting, scaling, failure modes
   - Security → Threat model, auth/authz, compliance
   - Support → Documentation, debugging tools, common issues
   - Analytics → Events to track, metrics to capture

3. IDENTIFY conflicts:
   - Business wants fast delivery vs Ops wants reliability
   - Product wants features vs Security wants constraints
   - Users want simplicity vs Power users want flexibility

4. RESOLVE conflicts explicitly:
   - Document trade-off decisions
   - Explain prioritization rationale
   - Get stakeholder buy-in
```

**Recognition Pattern for Incomplete Analysis:**

```
❌ INCOMPLETE: Spec only describes WHAT to build (product view)

✅ COMPLETE: Spec describes:
   - WHAT to build (product)
   - HOW it's testable (QA)
   - HOW it's operable (SRE)
   - HOW it's secure (security)
   - HOW users will use it (UX)
   - HOW support will handle issues (support)
   - WHAT data we'll collect (analytics)
   - HOW it integrates (engineering)
```

**Invoke: `conceptual-analysis`**

Ensure understanding of actual purpose, not just stated requirements:

```
□ What is the actual PURPOSE of this requirement?
□ Does this serve a functional need or match a pattern?
□ What would be LOST if requirement was removed/changed?
□ Is this the same CONCEPT differently expressed?
□ Are there hidden needs not explicitly stated?
```

**Exit Criteria:** All relevant stakeholders analyzed, conflicts identified and resolved, requirements
captured from each perspective

## Phase 4: Systematic Completeness Verification

**Invoke: `deliverable-completeness`**

Verify specification across all six dimensions. Quick path can skip Dimensions 4-6 for simple features.

### Dimension 1: Functional Completeness (ALL PATHS)

_All states, transitions, and outcomes covered_

```
Verification checklist:
✅ What are ALL possible states? (not just happy path)
  - Initial state, intermediate states, terminal states
  - Error states, loading states, retrying states

✅ What triggers transitions between states?
  - User actions
  - System events
  - External triggers
  - Timeout conditions

✅ Are there implicit states not mentioned?
  - Canceling, suspended, archived

✅ What happens on partial completion?
  - Cleanup requirements
  - Rollback strategy
  - Resume capability

Evidence of completeness:
- State machine diagram or table
- User stories with Given/When/Then acceptance criteria
- Business rules as numbered list
- Edge cases enumerated with expected behavior
```

### Dimension 2: Data Completeness (ALL PATHS)

_All data requirements specified_

```
Verification checklist:
✅ Input data:
  - Format, validation, constraints
  - Required vs optional fields
  - Default values
  - Validation rules (ranges, patterns, cross-field)

✅ Stored data:
  - Schema with data types
  - Relationships to other entities
  - Uniqueness constraints
  - Lifecycle (created, updated, deleted)
  - Audit requirements (who/when changed)

✅ Output data:
  - Structure, transformations
  - Filtering/pagination requirements

✅ Data sources and sinks:
  - Where data comes from
  - Where data goes to
  - Format conversions needed
```

### Dimension 3: Error & Edge Case Completeness (ALL PATHS)

_All failure modes and boundaries handled_

```
Error taxonomy verification:
✅ Validation Errors - Invalid input
✅ State Errors - Invalid operation for current state
✅ Resource Errors - Not found, already exists, quota exceeded
✅ External Errors - API failures, timeouts, network issues
✅ System Errors - Database down, out of memory
✅ Authorization Errors - Permission denied, expired session
✅ Concurrency Errors - Race conditions, conflicts
✅ Data Errors - Corruption, inconsistency

For EACH error type:
✅ Detection mechanism (how do we know it occurred?)
✅ User-facing message (what does user see?)
✅ Recovery action (can user retry? What changes?)
✅ System behavior (rollback? log? alert?)
✅ Edge case handling (partial success, timeout during recovery)

Edge case discovery:
- What if it's the FIRST time? (empty state)
- What if it's the LAST time? (cleanup, finalization)
- What if it's the ONLY one? (no pagination)
- What if there are MANY? (performance, limits)
- What if it's ALREADY done? (idempotency)
- What if it's CONCURRENT? (race conditions)
- What if it FAILS HALFWAY? (partial state)
- What if EXTERNAL dependency fails? (degradation)
```

### Dimension 4: Non-Functional Completeness (STANDARD+ PATHS)

_Quality attributes and operational requirements_

```
Performance verification:
✅ Latency requirements (p50, p95, p99)
✅ Throughput requirements (requests/sec, data volume)
✅ Scalability targets (concurrent users, data growth)
✅ Resource limits (memory, CPU, storage)

Security verification:
✅ Authentication requirements
✅ Authorization model (RBAC, ABAC)
✅ Data sensitivity classification
✅ Encryption requirements (in-transit, at-rest)
✅ Audit logging requirements
✅ Compliance requirements (GDPR, HIPAA)

Reliability verification:
✅ Availability targets (uptime SLA)
✅ Durability requirements (data loss tolerance)
✅ Backup/recovery requirements (RPO, RTO)
✅ Fault tolerance (graceful degradation)

Operability verification:
✅ Monitoring requirements (metrics, alerts)
✅ Logging requirements (what to log, retention)
✅ Debugging capabilities (trace IDs, debug mode)
✅ Configuration management (feature flags, env vars)
✅ Deployment requirements (zero-downtime, rollback)
```

### Dimension 5: Integration Completeness (STANDARD+ PATHS)

_All interactions with other systems specified_

```
For each external system:
✅ What data flows in/out?
✅ What's the protocol/format? (REST, gRPC, events)
✅ What's the authentication mechanism?
✅ What's the error handling? (retry, circuit breaker, fallback)
✅ What are the rate limits?
✅ What's the SLA/availability expectation?
✅ What happens if it's unavailable? (degradation strategy)
✅ How do we test without the real system? (mocking, staging)

Dependency classification:
□ SYNCHRONOUS or ASYNCHRONOUS?
  - Sync: Timeout? Retry strategy?
  - Async: Delivery guarantees? Ordering? Idempotency?

□ REQUIRED or OPTIONAL?
  - Required: System can't function without it (circuit breaker)
  - Optional: System degrades gracefully

□ UPSTREAM or DOWNSTREAM?
  - Upstream: We depend on it (protect with defensive patterns)
  - Downstream: It depends on us (maintain backward compatibility)
```

### Dimension 6: Temporal Completeness (STANDARD+ PATHS)

_Time-based concerns and lifecycle_

```
Scheduling verification:
✅ When should this happen? (trigger conditions)
✅ How often? (frequency, cron schedule)
✅ What if it misses a scheduled run? (catch-up, skip)

Ordering verification:
✅ Does order matter? (FIFO, priority, dependencies)
✅ What if events arrive out-of-order?
✅ What if the same event arrives twice? (idempotency)

Expiration verification:
✅ Does this data expire? (TTL, soft delete, hard delete)
✅ What triggers cleanup? (scheduled job, lazy deletion)
✅ What happens to references when expired?

Versioning verification:
✅ Do we need to support multiple versions?
✅ How do we migrate between versions?
✅ What's the deprecation policy?

Concurrency verification:
✅ Can this be done in parallel?
✅ What if two users do this simultaneously?
✅ What's the consistency model? (strong, eventual, causal)
```

**Quick Verification Protocol:**

```
For each dimension:
[ ] Have I shown EVIDENCE of completeness?
[ ] Can I point to SPECIFIC sections addressing this?
[ ] Are there GAPS I'm papering over with "seems complete"?

Insufficient evidence (checkbox theater):
❌ "Feature described" (no acceptance criteria)
❌ "States mentioned" (no structured state machine)
❌ "Errors handled" (no specific scenarios enumerated)
❌ "Fast enough" (no quantified targets)
```

**Exit Criteria:** All applicable dimensions verified with evidence, gaps documented explicitly

## Phase 4.5: Deep Information Gathering (COMPREHENSIVE PATH ONLY)

**Invoke: `information-completeness`**

For high-stakes features, systematically gather information across all 9 dimensions:

```
1. Intended State (What SHOULD BE)
   □ Requirements/specifications reviewed
   □ Design documents examined
   □ Standards/guidelines identified
   □ Architectural principles understood

2. Actual State (What IS)
   □ Current system behavior observed
   □ Codebase state analyzed
   □ Configuration examined
   □ Performance metrics gathered

3. Verified Facts (What's PROVEN)
   □ Test results reviewed
   □ Profiling data analyzed
   □ Benchmarks examined
   □ Proven behavior documented

4. Historical Development (WHY Current State Exists)
   □ Commit history reviewed
   □ Design decision records read
   □ Refactoring history understood
   □ Previous alternatives considered documented

5. Known Limitations (ACKNOWLEDGED Gaps)
   □ Technical debt documented
   □ Known bugs cataloged
   □ Planned deprecations identified
   □ Performance limitations understood

6. Usage Reality (How ACTUALLY Used)
   □ Actual usage patterns observed
   □ Workarounds documented
   □ Emergent patterns identified
   □ Real-world constraints understood

7. Stakeholder Understanding (What Others KNOW)
   □ Team expertise levels assessed
   □ User assumptions documented
   □ Maintainer knowledge captured
   □ Onboarding expectations understood

8. Related Information (Broader CONTEXT)
   □ Dependent systems identified
   □ Platform constraints documented
   □ Integration requirements understood
   □ Ecosystem considerations noted

9. Resources & Constraints (What's FEASIBLE)
   □ Time/budget constraints documented
   □ Team expertise assessed
   □ Infrastructure limitations understood
   □ Technical constraints documented
   □ Backward compatibility needs identified
```

**Completeness Checklist:**

```markdown
## Information Gathering Status

| Dimension         | Status   | Notes              |
| ----------------- | -------- | ------------------ |
| 1. Intended State | ✅/⚠️/❌ | [what I know/need] |
| 2. Actual State   | ✅/⚠️/❌ | [what I know/need] |
| 3. Verified Facts | ✅/⚠️/❌ | [what I know/need] |
| 4. Historical Dev | ✅/⚠️/❌ | [what I know/need] |
| 5. Known Limits   | ✅/⚠️/❌ | [what I know/need] |
| 6. Usage Reality  | ✅/⚠️/❌ | [what I know/need] |
| 7. Stakeholder    | ✅/⚠️/❌ | [what I know/need] |
| 8. Related Info   | ✅/⚠️/❌ | [what I know/need] |
| 9. Resources      | ✅/⚠️/❌ | [what I know/need] |

**Gaps:** [list significant gaps]
**Confidence:** [assessment given gaps]
```

**Handling Incomplete Information:**

```
When significant gaps exist:
1. Document what you DO know (completed dimensions)
2. State gaps explicitly: "Cannot verify X because Y"
3. Ask stakeholder: "Proceed with partial info, or is more available?"
4. Provide conditional recommendation:
   "Based on available info: X
    If [gap] reveals Y, conclusion changes to Z"
```

**Exit Criteria:** All 9 dimensions checked, gaps documented, confidence calibrated to information
completeness

## Phase 5: Quality Verification & Documentation Review

**Invoke: `documentation-quality`**

Ensure specification adds value and isn't useless documentation:

```
Core test for each section:
"If I remove this, what understanding is LOST?"

If answer is "nothing" → Section is useless
If answer is specific → Section has value

Categories to eliminate:
❌ Headers that restate structure ("Requirements Section")
❌ Descriptions that rephrase names ("User Service handles users")
❌ Comments describing WHAT instead of WHY
❌ Excessive visual decoration
❌ Information already derivable from context

What to keep:
✅ WHY decisions were made (rationale)
✅ Non-obvious constraints and trade-offs
✅ Business rules and validation logic
✅ Technical gotchas and warnings
✅ Context that new team members need
```

**Decision Framework:**

```
For each piece of documentation, ask in order:

1. Does it explain WHY, not WHAT?
   ✅ Keep: "Single-threaded to avoid race conditions"
   ❌ Delete: "Single-threaded implementation"

2. Does it provide non-obvious context?
   ✅ Keep: "Must call before initialize() due to DI order"
   ❌ Delete: "Configuration class" (name already says this)

3. Does it explain business rules or constraints?
   ✅ Keep: "Returns null for suspended users per GDPR"
   ❌ Delete: "Returns user or null"

4. Does it explain technical gotchas?
   ✅ Keep: "Uses weak refs to prevent memory leaks"
   ❌ Delete: "Uses weak references"

5. Would a new team member lose important information?
   ✅ Keep: "CRITICAL: Acquire lock before modifying"
   ❌ Delete: "Acquires lock" (obvious from: with lock:)

If ALL answers are NO → Delete it
```

**Quality Gates (Standard+ Paths):**

```
□ All user stories have acceptance criteria?
□ All states and transitions documented?
□ All business rules specified?
□ All edge cases identified?
□ Performance/security/ops requirements quantified?
□ All integrations have error handling specified?
□ No open blocking questions?
□ All requirements testable?
□ No useless documentation present?
```

**Exit Criteria:** Specification contains only valuable information, quality gates passed

## Phase 6: Evidence Validation (COMPREHENSIVE PATH ONLY)

**Invoke: `evidence-reasoning`**

For high-stakes features, validate all specification claims with evidence:

```
Protocol:
□ Every claim needs concrete supporting evidence
□ Show evidence BEFORE interpretation
□ Quote specific sources for assertions
□ Avoid assumption phrases

Forbidden phrases:
❌ "I assume..."
❌ "Typically means..."
❌ "Appears to..."
❌ "Should work..."
❌ "Standard practice..."

Required patterns:
✅ "Stakeholder confirmed: [quoted response]"
✅ "Documentation states: [quoted section]"
✅ "Analysis shows: [specific evidence]"
✅ "Testing revealed: [actual results]"

Decision framework:
1. Do I have direct evidence?
   YES → Quote it, then conclude
   NO → Gather evidence first

2. Can someone verify my claim?
   YES → Evidence is sufficient
   NO → Need more specific evidence

3. Am I interpreting or observing?
   INTERPRETING → Show what I observed first
   OBSERVING → Quote the observation directly
```

**Exit Criteria:** All specification claims backed by evidence, no unsupported assumptions

## Phase 7: Final Exit & Deliverable

### Completion Checklist

```
Before delivering specification:

PHASE COMPLETION:
[ ] Phase 1: Problem framing completed, path selected
[ ] Phase 2: Question levels completed (depth-appropriate)
[ ] Phase 3: Stakeholder analysis completed (scope-appropriate)
[ ] Phase 4: All applicable dimensions verified
[ ] Phase 4.5: Information gathering completed (if comprehensive)
[ ] Phase 5: Quality verification passed
[ ] Phase 6: Evidence validation completed (if comprehensive)

COMPLETENESS VERIFICATION:
[ ] All requirements listed?
[ ] Each requirement has acceptance criteria?
[ ] All stakeholder concerns addressed?
[ ] All dimensions verified with evidence?
[ ] Gaps documented explicitly?
[ ] No outstanding blocking questions?
[ ] All assumptions validated or marked as assumptions?
[ ] Trade-offs and conflicts resolved?

QUALITY VERIFICATION:
[ ] Specification explains WHY, not just WHAT?
[ ] No useless documentation present?
[ ] Requirements are testable?
[ ] Non-functional requirements quantified?
[ ] All integrations have error handling?
[ ] Would stake reputation on completeness?
```

### Deliverable Structure

```markdown
# Feature Specification: [Name]

## Document Status

-   **Status:** Draft / Review / Approved
-   **Elicitation Path:** Quick / Standard / Comprehensive
-   **Primary Stakeholders:** [List]
-   **Created:** [Date]
-   **Last Updated:** [Date]

## Problem Statement

**Business Problem:** [What problem are we solving?]
**Root Cause:** [Why does this problem exist?]
**Desired Outcome:** [What business outcome is expected?]
**Success Metrics:** [How will we measure success?]

## Requirements Overview

### Functional Requirements

[Organized by feature/capability]

#### FR-1: [Requirement Name]

-   **Description:** [What this requirement achieves]
-   **Rationale:** [WHY this is needed]
-   **Acceptance Criteria:**
    -   Given [context]
    -   When [action]
    -   Then [expected outcome]
-   **Priority:** Critical / High / Medium / Low
-   **Stakeholders:** [Who needs this]

### Non-Functional Requirements

#### Performance

-   **Latency:** [p50, p95, p99 targets]
-   **Throughput:** [requests/sec, data volume]
-   **Scalability:** [concurrent users, growth targets]

#### Security

-   **Authentication:** [Mechanism]
-   **Authorization:** [Model and rules]
-   **Data Sensitivity:** [Classification]
-   **Compliance:** [Requirements]

#### Reliability

-   **Availability:** [Uptime SLA]
-   **Durability:** [Data loss tolerance]
-   **Recovery:** [RPO, RTO]

#### Operability

-   **Monitoring:** [Metrics to track]
-   **Alerting:** [Alert conditions]
-   **Logging:** [What to log, retention]
-   **Debugging:** [Capabilities needed]

## Data Model

### Entities

[For each entity]

#### [Entity Name]

| Field      | Type      | Required | Validation       | Default | Notes             |
| ---------- | --------- | -------- | ---------------- | ------- | ----------------- |
| field_name | data_type | Yes/No   | validation_rules | value   | rationale/gotchas |

**Relationships:** [To other entities]
**Lifecycle:** [Create, update, delete behavior]
**Audit:** [Tracking requirements]

## State Model

### States

-   **State 1:** [Description]
-   **State 2:** [Description]
-   **State N:** [Description]

### Transitions

| From State | Event/Action | To State | Validation    | Notes        |
| ---------- | ------------ | -------- | ------------- | ------------ |
| state_1    | action_name  | state_2  | preconditions | side effects |

### State Machine Diagram

[Visual representation if helpful]

## Error Handling

### Error Categories

#### [Error Type]: [Name]

-   **Detection:** [How we know it occurred]
-   **User Message:** [What user sees]
-   **Recovery:** [What user can do]
-   **System Behavior:** [Rollback, log, alert]
-   **Edge Cases:** [Special scenarios]

## Edge Cases

| Scenario            | Expected Behavior | Notes       |
| ------------------- | ----------------- | ----------- |
| First time          | [behavior]        | [rationale] |
| Only one item       | [behavior]        | [rationale] |
| Many items          | [behavior]        | [rationale] |
| Already completed   | [behavior]        | [rationale] |
| Concurrent requests | [behavior]        | [rationale] |
| Partial failure     | [behavior]        | [rationale] |

## Integration Points

### [System/Service Name]

-   **Purpose:** [What we use it for]
-   **Protocol:** [REST, gRPC, events, etc.]
-   **Authentication:** [Mechanism]
-   **Data Flow:** [In/out]
-   **Error Handling:** [Retry, fallback, circuit breaker]
-   **Dependency Type:** [Required/Optional, Sync/Async, Upstream/Downstream]
-   **SLA:** [Availability expectation]
-   **Unavailability Strategy:** [Degradation approach]
-   **Testing:** [How to test without real system]

## Stakeholder Analysis

### Product Owner / Business

-   **Concerns:** [List]
-   **Success Criteria:** [What makes this successful]
-   **Requirements:** [Specific to this stakeholder]

### End User

-   **Concerns:** [List]
-   **User Journey:** [Step-by-step flow]
-   **Requirements:** [Specific to this stakeholder]

### [Additional Stakeholders]

[Follow same structure for: Developer, QA, Operations, Security, Support, Analytics]

## Trade-offs & Decisions

### Decision 1: [Title]

-   **Options Considered:** [A, B, C]
-   **Selected:** [Option X]
-   **Rationale:** [Why this was chosen]
-   **Trade-offs:** [What we're accepting/rejecting]
-   **Stakeholder Agreement:** [Who approved]

## Open Questions & Assumptions

### Blocking Questions

-   **Q1:** [Question that must be answered before implementation]
-   **Q2:** [Question that must be answered before implementation]

### Non-Blocking Questions

-   **Q3:** [Question that can be deferred]
-   **Q4:** [Question that can be deferred]

### Assumptions (REQUIRES VALIDATION)

1. [Assumption statement]
    - **Impact if wrong:** [What changes]
    - **Validation plan:** [How to validate]

## Out of Scope

[Explicitly list what is NOT included to prevent scope creep]

-   [Item 1]
-   [Item 2]

## Appendices

### Appendix A: Information Completeness Matrix

[For comprehensive path]

[Include 9-dimension table from Phase 4.5]

### Appendix B: Evidence Log

[For comprehensive path]

| Claim           | Evidence Source        | Date Verified | Notes     |
| --------------- | ---------------------- | ------------- | --------- |
| claim_statement | [stakeholder/doc/test] | [date]        | [context] |

### Appendix C: Stakeholder Conflict Resolution

[Document any conflicts found and how they were resolved]
```

## Decision Points & Branching Logic

### Decision Point 1: Depth Path Selection (Entry)

```
Assess complexity/stakes → Branch to appropriate path

IF simple feature + low risk + single stakeholder:
  → Quick Path (Phases 1-2-3-4-5)

ELSE IF moderate complexity + multi-stakeholder + standard ops:
  → Standard Path (Phases 1-2-3-4-5-6)

ELSE IF complex + high stakes + critical + novel:
  → Comprehensive Path (Phases 1-2-3-4-4.5-5-6-7)
```

### Decision Point 2: Question Level (Phase 2)

```
Based on selected path:

Quick Path:
  → Execute Levels 1-2 only
  → Exit when basic requirements clear

Standard Path:
  → Execute Levels 1-4
  → Exit when cross-cutting concerns addressed

Comprehensive Path:
  → Execute Levels 1-5 (full stakeholder perspective shift)
  → Exit when all perspectives analyzed
```

### Decision Point 3: Stakeholder Coverage (Phase 3)

```
Based on selected path:

Quick Path:
  → Analyze Product Owner, End User, Developer only
  → Exit when core perspectives covered

Standard Path:
  → Add QA, Operations, Security
  → Exit when operational concerns addressed

Comprehensive Path:
  → Include all 8 stakeholders
  → Exit when all perspectives analyzed and conflicts resolved
```

### Decision Point 4: Dimension Coverage (Phase 4)

```
Based on selected path:

Quick Path:
  → Verify Dimensions 1-3 only (Functional, Data, Error/Edge)
  → Exit when basic completeness achieved

Standard Path:
  → Verify all 6 dimensions
  → Exit when operational requirements specified

Comprehensive Path:
  → Verify all 6 dimensions + Phase 4.5 (9D information)
  → Exit when all information gathered and verified
```

### Decision Point 5: Information Gathering (After Phase 4)

```
IF comprehensive path AND high information uncertainty:
  → Execute Phase 4.5 (9-dimension information gathering)
  → Document gaps explicitly
  → Assess confidence

ELSE:
  → Skip to Phase 5 (Quality Verification)
```

### Decision Point 6: Evidence Validation (After Phase 5)

```
IF comprehensive path:
  → Execute Phase 6 (Evidence validation)
  → Validate all claims with evidence

ELSE:
  → Skip to Phase 7 (Final Exit)
```

## Error Handling & Recovery

### Error 1: Contradictory Stakeholder Requirements

**Detection:**

-   Stakeholder A requires X
-   Stakeholder B requires NOT X
-   Both are valid from their perspective

**Recovery:**

1. **Invoke: `stakeholder-analysis`** - Document conflict explicitly
2. Surface trade-offs to decision maker
3. Facilitate resolution meeting if needed
4. Document decision and rationale
5. Update specification with resolution
6. Get sign-off from both stakeholders

**Prevention:** Early stakeholder analysis (Phase 3) catches conflicts before implementation

### Error 2: Scope Creep During Elicitation

**Detection:**

-   New requirements emerging beyond original scope
-   "And also..." pattern in stakeholder responses
-   Timeline/resource estimates growing significantly

**Recovery:**

1. **Invoke: `framing-skepticism`** - Question if new requirements are essential
2. Document new requirements separately
3. Ask stakeholder: "Is this part of current scope or future enhancement?"
4. Create explicit "In Scope" vs "Out of Scope" vs "Future Consideration" sections
5. Reset expectations on delivery if scope expands

**Prevention:** Clear scope definition in Phase 1, explicit scope boundaries documented

### Error 3: Unanswered Blocking Questions

**Detection:**

-   Stakeholder unable/unwilling to answer critical questions
-   Questions remain unanswered after multiple attempts
-   Proceeding would require significant assumptions

**Recovery:**

1. **Invoke: `clarifying-questions`** - Make assumptions explicit
2. Document blocking questions prominently
3. Provide conditional specification: "If X then Y, else Z"
4. Ask stakeholder: "Proceed with assumptions or wait for answers?"
5. Track assumptions and validation plan
6. Set review checkpoint when answers available

**Prevention:** Early question asking (Phase 2), prioritize blocking questions

### Error 4: False Sense of Completeness

**Detection:**

-   All sections filled but feel "checkbox theater"
-   Statements are generic ("handle errors appropriately")
-   No specific numbers or examples
-   Passing completeness checks but lacking substance

**Recovery:**

1. **Invoke: `evidence-reasoning`** - Require evidence for all claims
2. **Invoke: `deliverable-completeness`** - Re-verify each dimension with evidence
3. Challenge vague statements: "What specifically does 'handle appropriately' mean?"
4. Convert generics to specifics with stakeholder
5. Add concrete examples and scenarios

**Prevention:** Evidence-based verification throughout (Phases 4-6), quality gates in Phase 5

### Error 5: Missing Stakeholder Perspective

**Detection:**

-   Implementation starts
-   Stakeholder X raises concerns: "This doesn't account for Y"
-   Y was never discussed during elicitation
-   Rework required

**Recovery:**

1. **Invoke: `stakeholder-analysis`** - Identify missed perspective
2. Halt implementation if significant impact
3. Conduct targeted elicitation with missed stakeholder
4. Update specification with new requirements
5. Assess implementation impact
6. Adjust timeline if needed

**Prevention:** Systematic stakeholder identification in Phase 3, comprehensive path for
multi-stakeholder features

## Iterative Refinement Loop

```
This workflow supports iterative refinement:

Initial Pass (Quick Path):
  → Get basic requirements
  → Identify areas of uncertainty
  → Flag need for deeper analysis

IF high uncertainty areas identified:
  → Upgrade to Standard Path for those areas
  → Re-run Phases 2-4 with more depth

IF critical unknowns remain:
  → Upgrade to Comprehensive Path for critical areas
  → Execute full depth analysis

The workflow is NOT strictly linear - areas can be revisited with
greater depth as uncertainty is discovered.
```

## Anti-Patterns

```
❌ Accept initial requirements at face value (skip framing skepticism)
❌ Skip stakeholder analysis ("I know what users want")
❌ Assume "reasonable defaults" without validation
❌ Fill gaps with "industry standard practices" unverified
❌ Only ask questions when stuck (reactive vs proactive)
❌ Skip edge case analysis ("we'll handle that later")
❌ Declare complete without systematic verification
❌ Only gather product owner perspective
❌ Trust familiar patterns without validation
❌ Write useless documentation to feel complete
❌ Make claims without evidence
❌ Choose comprehensive path when quick path sufficient (resource waste)
❌ Choose quick path when comprehensive path needed (risk acceptance)

✅ Challenge task framing before accepting constraints
✅ Systematic stakeholder analysis from start
✅ ASK, DON'T ASSUME at every level
✅ Proactive question generation before implementation
✅ Explicit edge case enumeration
✅ Evidence-based completeness verification
✅ Multi-perspective requirements gathering
✅ Validate familiar patterns (highest risk)
✅ Only document what adds value
✅ Evidence for all specification claims
✅ Select depth path appropriate to stakes
✅ Upgrade path depth when uncertainty discovered
```

## Integration with Other Skills

This workflow orchestrates atomic skills at each phase:

-   **Phase 1:** `pre-task-checkpoint` + `framing-skepticism`
-   **Phase 2:** `specification-elicitation` + `clarifying-questions`
-   **Phase 3:** `stakeholder-analysis` + `conceptual-analysis`
-   **Phase 4:** `deliverable-completeness`
-   **Phase 4.5:** `information-completeness` (comprehensive path)
-   **Phase 5:** `documentation-quality`
-   **Phase 6:** `evidence-reasoning` (comprehensive path)

When atomic skills are invoked, their full protocols apply.

## When NOT to Use This Workflow

```
Don't use for:
- Bug fixes (unless symptoms indicate deeper requirements issue)
- Simple enhancements to well-understood features
- Internal refactoring without user-facing changes
- Pure research/investigation tasks
- Documentation updates

DO use for:
- New features or capabilities
- Significant enhancements with cross-functional impact
- Unclear or ambiguous requirements
- High-stakes or mission-critical features
- Features requiring multi-stakeholder coordination
- Replacing existing features with new approaches
```

## Meta-Principle

```
Requirements quality = Question quality × Stakeholder coverage × Verification depth

Incomplete requirements lead to:
- Wrong implementations (built wrong thing)
- Rework cycles (discovered gaps too late)
- Stakeholder misalignment (unmet expectations)
- Operational issues (non-functional concerns missed)

The cost of thorough elicitation upfront << The cost of fixing assumption-driven errors

Transform "brief notes" into "complete specifications" through:
1. Systematic question-driven exploration
2. Multi-stakeholder perspective analysis
3. Dimensional completeness verification
4. Evidence-based validation

Each phase builds on the previous, ensuring nothing is missed.
```
