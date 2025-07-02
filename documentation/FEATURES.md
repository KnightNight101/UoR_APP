# UoR_APP Features & Architecture

## Full Featureset

### Core Features (Implemented/Planned)
- Project, task, and subtask management
- Team member management and permissions
- Sprint planning, prioritization, and daily planning
- Secure authentication (username, password, 2FA)
- Local-first, offline-capable design
- Dockerized deployment

### LLM/ML-Powered & Advanced Features (Planned)
- Modular LLM/ML-powered workflows
- Task delegation to local or server LLMs based on complexity
- Pluggable model system (swap models at backend, no client changes)
- Secure communication (HTTPS, gRPC)
- Load balancing for LLM inference
- No direct LLM chat: all model interactions are predefined and passive
- Version control: monitors changes, auto-generates commit messages, logs for team leads
- Analytics: bottleneck detection, task delay analysis, feedback-driven improvements
- Embedded tools: LibreOffice and VSCode integration for native editing
- Context switching: project summaries, task familiarization, knowledge base
- Feedback tools: suggestion box, bug report form, analytics pipeline

### User Roles
- **Employee:** Uses client app, views projects/tasks, submits feedback and daily reports
- **IT Infrastructure Team:** Accesses logs, model configs, server status, manages LLM deployments

### Authentication & Identity Management
- Username + password + 2FA
- User profiles: project memberships, schedules, task history, role-based permissions

### Core Workflows
- **Task Lifecycle & Planning:** BVA, subtask suggestion, prioritization, sprint planning
- **Daily Operations:** Auto-generated daily plan (Eisenhower Matrix), embedded tools, VCS, end-of-day reflection
- **Context Switching:** Project context summary, task familiarization
- **System Feedback:** Continuous analysis, feature rollout, feedback integration

### Optional/ML-Enhanced Features
- Commit message summarization from code diffs
- Task similarity matching for auto-subtasking
- Project health reports (velocity, blockers)
- Per-user workstyle adaptation
- Personal task memory ("you handled similar task in Q1")

---

## Architecture Overview

- **Client App:** React UI, to-do interface, embedded tools, local task execution, context workflows
- **Server App:** Node.js/Express backend, project/task DB, sprint planner, knowledge base, LLM executor, admin dashboard
- **LLM Infrastructure:** Modular execution, task allocation, predefined prompt chains

---

## Diagrams

### High-Level Architecture

```mermaid
flowchart LR
    subgraph ClientApp [Client Application]
        Login[Login & Authentication]
        ToDo[Daily To-Do List]
        Value[Value Analysis]
        Prioritize[Task Prioritization]
        Sprint[Sprint Planning]
        Summary[Project Summary]
    end

    subgraph LLMServer [LLM Server]
        LLMBackend[LLM Backend]
        ModelMgmt[Model Management]
        LLM1[LLM]
        LLM2[LLM]
        LLM3[LLM]
    end

    subgraph AppServer [Server]
        UserMgmt[User Management]
        ProjectMgmt[Project Management]
        TaskSched[Task Scheduling]
        KB[Knowledge Base]
    end

    subgraph AdminLLM [LLM Admin]
        AdminModelMgmt[Model Management]
        AdminLLM1[LLM]
        AdminLLM2[LLM]
        AdminLLM3[LLM]
    end

    User((Employee))
    ITTeam((IT Infrastructure Team))

    User -->|Uses| ClientApp
    User -->|Feedback| LLMServer

    ClientApp -->|HTTPS| LLMServer
    ClientApp -->|Event Logs| AdminLLM
    LLMServer -->|HTTPS| AppServer
    AdminLLM -->|HTTPS| AppServer

    LLMServer --> LLMBackend
    LLMServer --> ModelMgmt
    LLMServer --> LLM1
    LLMServer --> LLM2
    LLMServer --> LLM3

    AdminLLM --> AdminModelMgmt
    AdminLLM --> AdminLLM1
    AdminLLM --> AdminLLM2
    AdminLLM --> AdminLLM3

    AppServer --> UserMgmt
    AppServer --> ProjectMgmt
    AppServer --> TaskSched
    AppServer --> KB
```

---

## How to Contribute

- See the [README](../README.md) for setup and demo instructions.
- Open issues or pull requests for new features, bug fixes, or documentation improvements.
- Roadmap and open issues are tracked here.

---

## See Also

- [Project Brief](PROJECT_BRIEF.md)