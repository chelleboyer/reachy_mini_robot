# 📚 Documentation Index

This folder contains all project documentation for the Reachy Mini robot project.

## 📁 Directory Structure

### `/PRD.md`
**Product Requirements Document** - Core vision and requirements for Reachy Mini 2.0
- Product overview and goals
- User personas
- System architecture
- Functional & non-functional requirements
- Product roadmap (v1-v3)

### `/master-documentation-ideation/`
**Architecture & Design Documentation**
- `arch-mvp-scope-epics-stories.md` - Full system architecture, MVP scope, epics & user stories
- `rmlg-ideation.md` - LangGraph brain ideation and node design
- `state-object-brain.md` - BrainState schema and data structures
- `diagram-nodes-edges.md` - Detailed node and edge definitions
- `high-level-graph-diagram.mermaid` - Visual system diagrams
- `runtime-behaviors-sequencing.md` - Behavior sequencing logic
- `production-grade-plan.md` - Production readiness and robustness plan
- `eval-ai-level.md` - AI evaluation criteria
- `eval-system-level.md` - System-level evaluation
- `master-documentation-summary.md` - Documentation overview
- `master-documentation-table-of-contents.md` - Table of contents

### `/sprint-artifacts/`
**Sprint Planning & Project Workflow**
- `WORKFLOW.md` - Overall development workflow guide
- `SPRINT_TEMPLATE.md` - Sprint planning template

### `/reachy-mini-ranger/`
**Ranger App Development Documentation**
- `RANGER_WORKFLOW.md` - Complete workflow guide for ranger app development
- `TASK_BOARD.md` - Task tracking and feature backlog
- `TESTING.md` - Testing guide (unit, integration, hardware)

## 🎯 Quick Navigation

### For App Developers (Ranger)
Start here if you're working on the **reachy_mini_ranger** app:
1. Read [`/reachy-mini-ranger/RANGER_WORKFLOW.md`](./reachy-mini-ranger/RANGER_WORKFLOW.md)
2. Check [`/reachy-mini-ranger/TASK_BOARD.md`](./reachy-mini-ranger/TASK_BOARD.md) for tasks
3. Follow [`/reachy-mini-ranger/TESTING.md`](./reachy-mini-ranger/TESTING.md) for testing

### For LangGraph Brain Development
Start here if you're working on the **AI brain architecture**:
1. Read [`/PRD.md`](./PRD.md) for vision
2. Review [`/master-documentation-ideation/arch-mvp-scope-epics-stories.md`](./master-documentation-ideation/arch-mvp-scope-epics-stories.md)
3. Study [`/master-documentation-ideation/rmlg-ideation.md`](./master-documentation-ideation/rmlg-ideation.md)

### For Sprint Planning
1. Use [`/sprint-artifacts/SPRINT_TEMPLATE.md`](./sprint-artifacts/SPRINT_TEMPLATE.md)
2. Follow [`/sprint-artifacts/WORKFLOW.md`](./sprint-artifacts/WORKFLOW.md)

## 📖 SDK Reference Documentation

SDK documentation is in **`src-refs/reachy_mini/docs/`** (read-only reference):
- `python-sdk.md` - Python SDK usage
- `rest-api.md` - REST API reference
- `troubleshooting.md` - Common issues and solutions
- `wireless-version.md` - Wireless setup
- `RPI.md` - Raspberry Pi setup

**Note:** Do not modify files in `src-refs/` - they are reference implementations only!

## 🚀 Getting Started

### New to the Project?
1. Read [`/PRD.md`](./PRD.md) - Understand the vision
2. Read [`/sprint-artifacts/WORKFLOW.md`](./sprint-artifacts/WORKFLOW.md) - Learn the process
3. Choose your focus area:
   - **App Development** → Go to `/reachy-mini-ranger/`
   - **Brain Architecture** → Go to `/master-documentation-ideation/`

### Ready to Code?
- **Ranger App:** See [`/reachy-mini-ranger/RANGER_WORKFLOW.md`](./reachy-mini-ranger/RANGER_WORKFLOW.md)
- **New Sprint:** Use [`/sprint-artifacts/SPRINT_TEMPLATE.md`](./sprint-artifacts/SPRINT_TEMPLATE.md)

## 📊 Documentation Status

| Document | Status | Last Updated |
|----------|--------|--------------|
| PRD | ✅ Complete | Dec 2025 |
| Architecture | ✅ Complete | Dec 2025 |
| Ranger Workflow | ✅ Complete | Dec 9, 2025 |
| Sprint Template | ✅ Complete | Dec 9, 2025 |
| Task Board | 🔄 In Progress | Dec 9, 2025 |

## 🔗 External Resources

- **Repository:** pollen-robotics/reachy_mini
- **Branch:** develop
- **SDK Examples:** `src-refs/reachy_mini/examples/`
- **BMAD Tools:** `.bmad/bmb/workflows/`

---

*Documentation structure initialized: December 9, 2025*
