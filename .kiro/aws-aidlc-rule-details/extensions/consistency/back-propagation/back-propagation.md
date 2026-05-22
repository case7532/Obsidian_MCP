# Back-Propagation Consistency Rules

## Overview
These rules ensure that all AI-DLC documents remain synchronized when changes occur at any level. They are cross-cutting constraints that apply during Construction and late Inception phases.

**Enforcement**: At each applicable stage, the model MUST verify compliance with these rules before presenting the stage completion message to the user.

### Blocking Consistency Finding Behavior
A **blocking consistency finding** means:
1. The finding MUST be listed in the stage completion message under a "Consistency Findings" section with the CONSISTENCY rule ID and description
2. The stage MUST NOT present the "Continue to Next Stage" option until all blocking findings are resolved
3. The model MUST present only the "Request Changes" option with a clear explanation of what needs to change
4. The finding MUST be logged in `aidlc-docs/audit.md` with the CONSISTENCY rule ID, description, and stage context

### Default Enforcement
All rules in this document are **blocking** by default.

---

## Rule CONSISTENCY-01: Upstream Impact Check on Document Update

**Rule**: Every time a design document, functional design, NFR design, or infrastructure design is updated, the model MUST:
1. Identify which upstream documents could be affected (requirements, user stories, application design)
2. Check whether the change introduces inconsistency with those upstream documents
3. If inconsistency is found, prompt the user before proceeding with a summary of what needs to change upstream

**Applies to stages**: Functional Design, NFR Design, Infrastructure Design, Code Generation

**Verification**:
- No design document is updated without an upstream impact assessment
- User is prompted when upstream inconsistency is detected
- Impact assessment is logged in audit.md

---

## Rule CONSISTENCY-02: Design Decision Reflection During Code Generation

**Rule**: When a design decision is made or discovered during code generation that is not reflected in the design documents, the model MUST:
1. Pause code generation
2. Update the relevant design document to reflect the decision
3. Check upstream impact per CONSISTENCY-01
4. Resume code generation only after documentation is updated

**Applies to stages**: Code Generation

**Verification**:
- No code is generated based on undocumented design decisions
- Design documents are updated before code generation resumes

---

## Rule CONSISTENCY-03: Post-Unit Back-Propagation Sweep

**Rule**: After completing code generation for each unit, the model MUST perform a back-propagation sweep:
1. Review the unit's final design files
2. Compare against requirements and user stories
3. Identify any drift or undocumented changes
4. Present a consistency report to the user listing: aligned items, drifted items requiring upstream update, and new items not in original requirements

**Applies to stages**: Code Generation (at unit completion, before moving to next unit)

**Verification**:
- A consistency report is presented after each unit's code generation
- Drifted items are resolved before proceeding to the next unit or Build and Test
