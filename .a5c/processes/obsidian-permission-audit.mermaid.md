# obsidian-permission-audit — flow

```mermaid
flowchart TD
  S[Inputs: repoRoot, settings paths, reportPath] --> P1
  subgraph P1[Phase 1: Survey — parallel]
    A[survey-skill-allowed-tools<br/>@Explore]
    B[survey-agent-tools<br/>@Explore]
    C[survey-body-references<br/>@Explore]
    D[survey-settings-permissions<br/>@general-purpose]
  end
  P1 --> BP1{breakpoint:<br/>scope or skip ahead?}
  BP1 -->|approve| P2[classify-inconsistencies<br/>@general-purpose]
  BP1 -->|narrow| P2
  P2 --> P3[recommend-actions<br/>@general-purpose]
  P3 --> BP2{breakpoint:<br/>reweight priorities?}
  BP2 -->|approve| P4[write-report<br/>.docs/2026-05-31-obsidian-permission-audit.md]
  BP2 -->|adjust| P3
  P4 --> END([completion])
```
