# Decision Log

## Decision status

- **Proposed:** documented but not yet explicitly confirmed
- **Accepted:** approved for implementation
- **Superseded:** replaced by a later decision

| ID | Decision | Status | Rationale |
|---|---|---|---|
| D-001 | Build a responsive web application | Proposed | Supports mobile and desktop with one MVP |
| D-002 | Use Python and FastAPI for application services | Proposed | Fits the existing Python recommender |
| D-003 | Use custom HTML, CSS, and JavaScript for the initial UI | Proposed | Enables a distinctive interface without a large client toolchain |
| D-004 | Do not require an account in the MVP | Proposed | Reduces setup and keeps discovery immediate |
| D-005 | Keep user-added songs private | Proposed | Protects ownership and simplifies moderation |
| D-006 | Delete uploaded audio after analysis by default | Proposed | Minimizes retained copyrighted and private data |
| D-007 | Provide AI analysis and full manual entry | Accepted | Requested product requirement |
| D-008 | Require review before saving AI-estimated features | Accepted | Prevents uncertain estimates from becoming silent facts |
| D-009 | Use RAG plus deterministic feature scoring | Accepted | Makes retrieval central while retaining explainability |
| D-010 | Provide deterministic fallback and demo mode | Accepted | Required for reliability and reproducibility |
| D-011 | Exclude commercial streaming and social features from MVP | Proposed | Keeps the applied-AI scope achievable |
| D-012 | Use VYBE as the working name | Proposed | Brand and trademark review remain future work |

## Decisions required before Phase 2

The product owner should confirm or change D-001 through D-006, D-011, and
D-012. Accepted technical decisions may still be superseded if Phase 2
compatibility checks identify a blocking constraint.
