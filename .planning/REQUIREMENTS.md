# Requirements: Daily Learning — n8n Email Workflow

**Defined:** 2026-06-13
**Core Value:** A question lands in the inbox every morning — no setup friction, no AI dependency, no gaps.

## v1 Requirements

### Sheet Setup

- [ ] **SHEET-01**: Bank tab has columns: question, domain, est_minutes, status, date_sent
- [ ] **SHEET-02**: All 130 questions from questions.md imported into Bank tab with status = queued

### Workflow

- [ ] **WF-01**: Single n8n workflow with cron trigger at 06:30 daily
- [ ] **WF-02**: Reads Bank tab, filters status = queued, picks 3 in row order (oldest first)
- [ ] **WF-03**: Builds plain-text email — question, domain, est_minutes; no answers, no hints
- [ ] **WF-04**: Sends email via Gmail (OAuth)
- [ ] **WF-05**: Marks the 3 sent questions: status = sent, date_sent = today

## v2 Requirements

- **FUTURE-01**: Claude agent that edits the Bank tab (add/remove questions based on user input)

## Out of Scope

| Feature | Reason |
|---------|--------|
| AI question generation in workflow | Workflow is static logic only; Claude agent handles bank edits separately |
| Domains tab | Domain lives on the question row; no AI rotation logic needed |
| Queue depth top-up logic | Bank is pre-seeded with 130 questions; no Workflow A equivalent |
| Multiple workflows | Consolidating A + B into one; timing dependency removed |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| SHEET-01 | Phase 1 | Pending |
| SHEET-02 | Phase 1 | Pending |
| WF-01 | Phase 2 | Pending |
| WF-02 | Phase 2 | Pending |
| WF-03 | Phase 2 | Pending |
| WF-04 | Phase 2 | Pending |
| WF-05 | Phase 2 | Pending |

**Coverage:**
- v1 requirements: 7 total
- Mapped to phases: 7
- Unmapped: 0 ✓

---
*Requirements defined: 2026-06-13*
*Last updated: 2026-06-13 after roadmap creation*
