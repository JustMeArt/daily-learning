# Roadmap: Daily Learning — n8n Email Workflow

## Overview

Two phases of work: first restructure the Google Sheet into a single Bank tab seeded with all 130 questions, then build the n8n workflow that reads from it, composes a plain-text email with 3 questions, sends via Gmail, and marks those questions sent. When both phases are complete, a question lands in the inbox every morning automatically.

Milestone v1.1 Deploy adds three phases (4–6) that move n8n off the local machine onto a DigitalOcean VPS running Docker, so the 06:30 email arrives regardless of whether the local machine is on.

## Phases

**Phase Numbering:**
- Integer phases (1, 2, 3): Planned milestone work
- Decimal phases (2.1, 2.2): Urgent insertions (marked with INSERTED)

Decimal phases appear between their surrounding integers in numeric order.

- [x] **Phase 1: Sheet Setup** - Create and seed the Bank tab with all 130 questions
- [x] **Phase 2: Workflow** - Build n8n workflow that picks, emails, and marks 3 questions daily
- [x] **Phase 3: Curator Agent** - Claude-powered skill+agent that edits the question bank via natural language and syncs to the Google Sheet (completed 2026-06-13)
- [x] **Phase 4: VPS + Docker** - Provision a DigitalOcean Droplet, harden access, and install Docker (completed 2026-06-15)
- [x] **Phase 5: n8n Container** - Run n8n in a persistent, auto-restarting container and commit the compose file
- [x] **Phase 6: Wire + Verify** - Migrate credentials, activate the workflow, confirm live 06:30 delivery, document setup

## Phase Details

### Phase 1: Sheet Setup
**Goal**: The Google Sheet has a single Bank tab, correctly structured and seeded with all 130 questions ready to send
**Depends on**: Nothing (first phase)
**Requirements**: SHEET-01, SHEET-02
**Success Criteria** (what must be TRUE):
  1. Bank tab exists with exactly five columns: question, domain, est_minutes, status, date_sent
  2. All 130 questions from questions.md are present in the Bank tab with status = queued
  3. No other data tabs interfere — sheet has one clear Bank tab as the data source
**Plans**: TBD

### Phase 2: Workflow
**Goal**: A single n8n workflow runs every morning at 06:30, picks the 3 oldest queued questions, emails them, and marks them sent
**Depends on**: Phase 1
**Requirements**: WF-01, WF-02, WF-03, WF-04, WF-05
**Success Criteria** (what must be TRUE):
  1. Workflow triggers automatically at 06:30 daily without manual intervention
  2. Exactly 3 questions appear in the inbox email, in row order (oldest queued first), with no answers or hints
  3. Each emailed question shows domain and est_minutes alongside the question text in plain text
  4. After sending, those 3 rows in the Bank tab show status = sent and today's date in date_sent
  5. Running the workflow a second time on the same day picks the next 3 queued questions, not the already-sent ones
**Plans**: TBD

### Phase 3: Curator Agent
**Goal**: A Claude-powered agent the user can invoke with natural language to add, remove, or refine questions in the bank — writes to questions.md and syncs new rows to the Google Sheet Bank tab
**Depends on**: Phase 1, Phase 2
**Requirements**: FUTURE-01
**Success Criteria** (what must be TRUE):
  1. User can invoke the agent with a loose instruction ("add 5 volcano questions") and get correctly formatted questions added to questions.md
  2. New questions follow the daily-question-curator quality bar (specific, non-obvious, spoiler-free)
  3. New questions are also appended to the Google Sheet Bank tab with status = queued
  4. Removals by name or description are reflected in both questions.md and the sheet
  5. No duplicate questions are introduced
**Plans**: 3 plans
- [x] 03-01-PLAN.md — Repo foundations (.gitignore, .secrets/) and Python Sheets API helper script
- [x] 03-02-PLAN.md — Service account credential drop-in and live Bank tab verification
- [x] 03-03-PLAN.md — /curate-bank SKILL.md with preview gates and end-to-end add/remove verification

### Phase 4: VPS + Docker
**Goal**: A DigitalOcean Droplet is running, SSH-accessible, firewalled, and ready to run Docker containers
**Depends on**: Phase 3 (milestones complete)
**Requirements**: VPS-01, VPS-02, VPS-03, DOCK-01, DOCK-02
**Success Criteria** (what must be TRUE):
  1. User can SSH into the Droplet from their local machine using an SSH key (no password)
  2. Running `ufw status` shows only ports 22 and 5678 open; all other ports are denied
  3. Running `docker --version` and `docker compose version` on the VPS both return version strings without error
  4. Running `docker run hello-world` on the VPS completes successfully
**Plans**: 3 plans
- [ ] 04-01-PLAN.md — Provision DO Droplet (Ubuntu 24.04, 2 GiB) and verify ed25519 key-based root SSH
- [ ] 04-02-PLAN.md — Harden SSH (non-root sudo user, password auth off) and lock down ufw (22+5678 only, DOCKER-USER chain in after.rules)
- [ ] 04-03-PLAN.md — Install Docker Engine + docker-compose-plugin from Docker's official apt repo, enable on boot, run hello-world smoke test

### Phase 5: n8n Container
**Goal**: n8n is running inside a Docker container on the VPS, reachable at http://VPS-IP:5678, with persistent storage and automatic restart — and the compose file is committed to the repo
**Depends on**: Phase 4
**Requirements**: N8N-01, N8N-02, N8N-03, DEPLOY-01
**Success Criteria** (what must be TRUE):
  1. Navigating to http://VPS-IP:5678 in a browser shows the n8n login screen
  2. After restarting the container (`docker compose restart`), n8n data (accounts, settings) is still present
  3. After rebooting the VPS, the n8n container comes back up automatically without any manual intervention
  4. deploy/docker-compose.yml exists in the repo and is the exact file used to start the container
**Plans**: 2 plans
- [ ] 05-01-PLAN.md — Write and commit deploy/docker-compose.yml
- [ ] 05-02-PLAN.md — Copy to VPS, start n8n, verify access + persistence + auto-restart

### Phase 6: Wire + Verify
**Goal**: Gmail OAuth, Google Sheets credentials, and the daily-learning workflow are live in hosted n8n — and a real 06:30 email confirms end-to-end delivery from the VPS
**Depends on**: Phase 5
**Requirements**: CRED-01, CRED-02, CRED-03, VERIFY-01, VERIFY-02, DEPLOY-02
**Success Criteria** (what must be TRUE):
  1. Triggering the workflow manually from hosted n8n sends 3 questions to lfornefett@gmail.com without error
  2. The Bank tab in Google Sheets shows those rows marked sent after the manual trigger
  3. The 06:30 schedule is active in hosted n8n and the workflow runs automatically on the next scheduled fire
  4. deploy/setup.md documents every setup step taken, so the VPS can be reproduced from scratch
**Plans**: 3 plans
- [ ] 06-01-PLAN.md — Update Google Cloud Console callback URL + create OAuth2 credentials in hosted n8n
- [ ] 06-02-PLAN.md — Import workflow, test manual trigger, activate 06:30 schedule
- [ ] 06-03-PLAN.md — Write deploy/setup.md runbook

## Progress

**Execution Order:**
Phases execute in numeric order: 1 → 2 → 3 → 4 → 5 → 6

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Sheet Setup | 1/1 | Complete | 2026-06-13 |
| 2. Workflow | 1/1 | Complete | 2026-06-13 |
| 3. Curator Agent | 3/3 | Complete   | 2026-06-13 |
| 4. VPS + Docker | 3/3 | Complete | 2026-06-15 |
| 5. n8n Container | 2/2 | Complete | 2026-06-15 |
| 6. Wire + Verify | 3/3 | Complete | 2026-06-16 |
