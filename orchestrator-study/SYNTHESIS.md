# Orchestrator Patterns Study — Sept 23, 2026

> "The best applications are the ones the builders can't do without because they can't unsee the possibilities and advantages." — Casey

## The 5 patterns we can't unsee

Studied: K8s Operators, ArgoCD GitOps, Pulumi, AWS CDK, Terraform.

| # | Pattern | Source | Why we can't unsee it |
|---|---------|--------|-----------------------|
| 1 | **Reconciliation loop** | K8s Operators | `desired` vs `actual` state, diff, patch, idempotent. Foundation of self-healing systems. |
| 2 | **Sync waves + hooks** | ArgoCD | Order dependency resolution via integer waves + PreSync/Sync/PostSync phases. Without this, deployment ordering is invisible. |
| 3 | **Construct layers** (L1/L2/L3) | AWS CDK | Bare resources / opinionated defaults / patterns. Gives names to abstraction levels. |
| 4 | **Automation API** | Pulumi | Embed IaC in agent code via a programmatic SDK. The orchestrator becomes callable. |
| 5 | **App-of-Apps + ApplicationSet** | ArgoCD | One bootstrap declares many children. Fan-out via templates. |

## Mapping to OUR stack

| Pattern | Where it lives now | Where it should live |
|---------|-------------------|---------------------|
| Reconciliation loop | mavis-fleet RSILoop (substring) | mavis-fleet full Reconciler substrate |
| Sync waves | nowhere | ax-quilt cell annotations |
| Construct layers | implicit (cells/ranges/workbooks) | explicit L1=Cell, L2=Workbook, L3=Pattern |
| Automation API | nowhere | ax-quilt embedded SDK for agents |
| App-of-Apps | nowhere | ax-quilt WorkbookSet |

## What's most useful for OUR builders (us)

1. **Construct layers (L3 patterns)** — save us from re-authoring common workbooks. `IndustrialAuditPattern`, `ImagePipelinePattern`. **HIGH** — every workbook I write I want to be reusable.

2. **Reconciliation loop** — make mavis-fleet actually self-heal. Canon substrate should diff desired vs actual and patch. **HIGH** — without this, the substrate is read-only.

3. **Mixins** — apply cross-cutting features (encryption, observability, polyformality-canary) to any cell. **MEDIUM**.

4. **Sync waves** — order cell application in a workbook. **MEDIUM** — solves "this cell depends on that cell being up first."

5. **Automation API** — embed ax-quilt into agent code. **LOW** — we can defer; the CLI is enough.

## The build plan

Implement #1 (Patterns), #2 (Reconciler), and #4 (Sync waves) in this turn.

