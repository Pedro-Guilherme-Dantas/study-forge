# Implementation Plan: [FEATURE]

**Branch**: `[###-feature-name]` | **Date**: [DATE] | **Spec**: [link]

**Input**: Feature specification from `/specs/[###-feature-name]/spec.md`

**Note**: This template is filled in by the `/speckit-plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

[Extract from feature spec: primary requirement + technical approach from research]

## Technical Context

<!--
  ACTION REQUIRED: Replace the content in this section with the technical details
  for the project. The structure here is presented in advisory capacity to guide
  the iteration process.
-->

**Language/Version**: [e.g., Python 3.11, Swift 5.9, Rust 1.75 or NEEDS CLARIFICATION]

**Primary Dependencies**: [e.g., FastAPI, UIKit, LLVM or NEEDS CLARIFICATION]

**Storage**: [if applicable, e.g., PostgreSQL, CoreData, files or N/A]

**Testing**: [e.g., pytest, XCTest, cargo test or NEEDS CLARIFICATION]

**Target Platform**: [e.g., Linux server, iOS 15+, WASM or NEEDS CLARIFICATION]

**Project Type**: [e.g., library/cli/web-service/mobile-app/compiler/desktop-app or NEEDS CLARIFICATION]

**Performance Goals**: [domain-specific, e.g., 1000 req/s, 10k lines/sec, 60 fps or NEEDS CLARIFICATION]

**Constraints**: [domain-specific, e.g., <200ms p95, <100MB memory, offline-capable or NEEDS CLARIFICATION]

**Scale/Scope**: [domain-specific, e.g., 10k users, 1M LOC, 50 screens or NEEDS CLARIFICATION]

**Container Environment**: [Container-based dependency installation, services, build, tests and
evaluations; reproducible commands; host/container boundary, volumes and secret handling.
Do not install project dependencies or configure project runtimes/services on the host.]

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Use `.specify/memory/constitution.md` as the authority. Record evidence or a justified N/A for
each gate before research and again after design. Resolve violations through a compliant design
or an approved constitutional amendment before incompatible implementation.

- **Evidence and provenance**: Source consultation and citations are traceable; unsupported or
  conflicting evidence leads to an explicit limitation rather than invented support.
- **Trust boundaries**: Files, web pages and retrieved/tool content cannot change instructions
  or permissions; application/tool contracts enforce authority beyond prompts.
- **User-controlled persistence**: Only explicitly selected web sources can be ingested. Define
  temporary lifetime/disposal and check all stores, including history, summaries, logs, traces,
  caches, checkpoints and embeddings, for indirect retention of unselected content.
- **Agent contracts and deterministic ingestion**: Document responsibilities, inputs, outputs,
  permissions and handoffs. Validation, normalization, chunking and writes use versioned code
  rules; the application verifies source-specific user authorization before persistence.
- **Proportional complexity and diagnostics**: Justify added components against current needs
  and simpler alternatives; collect only diagnostic data allowed by retention and secret rules.
- **Quality evidence**: Map acceptance criteria to relevant tests and repeatable retrieval/agent
  evaluations where affected, including negative cases for the guarantees above.
- **Bounded execution and failures**: Define applicable time, tool-call, agent-cycle, data-volume
  and retry limits; distinguish partial/interrupted/completed states and protect write consistency.
- **Container isolation**: Configure and execute the project environment in containers with
  reproducible commands; reserve host use for editing, version control and container invocation.

Carry forward current scope into the feature spec: Markdown-only local uploads and the initial
orchestrator/researcher/tutor roles. Keep concrete technologies, thresholds and retention durations
in the spec/plan; do not infer unapproved choices from these gates.

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
├── plan.md              # This file (/speckit-plan command output)
├── research.md          # Phase 0 output (/speckit-plan command)
├── data-model.md        # Phase 1 output (/speckit-plan command)
├── quickstart.md        # Phase 1 output (/speckit-plan command)
├── contracts/           # Phase 1 output (/speckit-plan command)
└── tasks.md             # Phase 2 output (/speckit-tasks command - NOT created by /speckit-plan)
```

### Source Code (repository root)
<!--
  ACTION REQUIRED: Replace the placeholder tree below with the concrete layout
  for this feature. Delete unused options and expand the chosen structure with
  real paths (e.g., apps/admin, packages/something). The delivered plan must
  not include Option labels.
-->

```text
# [REMOVE IF UNUSED] Option 1: Single project (DEFAULT)
src/
├── models/
├── services/
├── cli/
└── lib/

tests/
├── contract/
├── integration/
└── unit/

# [REMOVE IF UNUSED] Option 2: Web application (when "frontend" + "backend" detected)
backend/
├── src/
│   ├── models/
│   ├── services/
│   └── api/
└── tests/

frontend/
├── src/
│   ├── components/
│   ├── pages/
│   └── services/
└── tests/

# [REMOVE IF UNUSED] Option 3: Mobile + API (when "iOS/Android" detected)
api/
└── [same as backend above]

ios/ or android/
└── [platform-specific structure: feature modules, UI flows, platform tests]
```

**Structure Decision**: [Document the selected structure and reference the real
directories captured above]

## Complexity Tracking

> **Fill ONLY when complexity needs justification. This table does not authorize a constitutional
> violation; resolve such violations through design changes or an approved amendment.**

| Added Complexity | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |
