# Project Plan

## Instruksjoner

1. Der hvor det står {prompt / user-input-file}, kan dere legge inn en egen prompt eller filnavn for å gi ekstra instruksjoner. Hvis dere ikke ønsker å legge til ekstra instruksjoner, kan dere bare fjerne denne delen.
2. Hvis jeg har skrevet noe der allerede, f.eks. "Root Cause Analysis and Solution Design for Player Inactivity", så kan dere bytte ut min prompt med deres egen.


## Fase 0

- [x] /run-agent-task analyst *workflow-init
  - [x] File: bmm-workflow-status.yaml
- [x] Brainstorming
  - [x] /run-agent-task analyst *brainstorm "Root Cause Analysis and Solution Design for Player Inactivity"
    - [x] File: brainstorming-session-results-2025-12-02.md
  - [x] /run-agent-task analyst *brainstorm "User Flow and journeys"
    - [x] File: brainstorming-session-results-thursday,-4-december-2025.md
- [x] Research
  - [x] Researched Decision Model for "Single Most Helpful Next Step"
    - [x] File: research-decision-model.md
  - [x] Researched First Interaction Patterns for Zero-Friction Learning
    - [x] File: research-first-interaction-patterns.md
  - [x] Researched Technical Constraints and Capabilities
    - [x] File: research-technical-constraints.md
- [x] Product Brief
  - [x] Created consolidated product brief from brainstorming, research, and proposal.
    - [x] File: product-brief.md

## Fase 1

- [x] Planning
  - [x] /run-agent-task pm *prd
    - [x] File: PRD.md
  - [] /run-agent-task pm *validate-prd
    - [] File: validation-report-2025-12-04-rerun.md
  - [x] /run-agent-task ux-designer *create-ux-design {docs/maode/ux-design-prompt}
    - [x] File: ux-design-specification.md
    - [x] File: ux-color-themes.html
    - [x] File: ux-design-directions.html
  - [x] /run-agent-task ux-designer *validate-ux-design {prompt / user-input-file}

## Fase 2

- [x] Solutioning
  - [x] /run-agent-task architect *create-architecture {prompt / user-input-file}
    - [x] File: architecture.md
  - [x] /run-agent-task pm *create-epics-and-stories {prompt / user-input-file}
    - [x] File: epics.md

  - [x] /run-agent-task architect *solutioning-gate-check {prompt / user-input-file}

## Fase 3

- [x] Implementation
  - [x] /run-agent-task sm *sprint-planning {prompt / user-input-file}
    - [x] File: sprint-artifacts/sprint-status.yaml
  - for each epic in sprint planning:
    - [x] /run-agent-task sm create-epic-tech-context {prompt / user-input-file}
      - [x] File: sprint-artifacts/tech-spec-epic-1.md
    - [x] /run-agent-task sm validate-epic-tech-context {prompt / user-input-file}
      - [x] File: sprint-artifacts/validation-report-2025-12-10.md
    - for each story in epic:
      - [x] /run-agent-task sm *create-story {prompt / user-input-file}
        - [x] File: sprint-artifacts/1-2-user-account-creation.md
      - [] /run-agent-task sm *validate-create-story {prompt / user-input-file}
      - [] /run-agent-task sm *create-story-context {prompt / user-input-file}
        - [] File: sprint-artifacts/{{story_key}}.context.xml5
      - [] /run-agent-task sm *validate-story-context {prompt / user-input-file}
      - [] /run-agent-task sm *story-ready-for-dev {prompt / user-input-file}
      while code-review != approved:
        - [ ] /run-agent-task dev *develop-story {prompt / user-input-file}
        - [ ] /run-agent-task dev *code-review {prompt / user-input-file}
      - [ ] /run-agent-task dev *story-done {prompt / user-input-file}
      - [ ] /run-agent-task sm *test-review {prompt / user-input-file}
    - [ ] /run-agent-task sm *epic-retrospective {prompt / user-input-file}





## BMAD workflow

<img src="images/bmad-workflow.svg" alt="BMAD workflow">