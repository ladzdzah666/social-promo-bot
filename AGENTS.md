# AGENTS.md

Master operational guidelines for AI coding agents (Antigravity IDE, Claude Code, Cursor, GitHub Copilot, OpenAI Codex, OpenCode) operating on the **social-promo-bot** repository.

This repository enforces production-grade software engineering standards adopted from **[Addy Osmani's Agent Skills](https://github.com/addyosmani/agent-skills)** and anti-AI-slop quality filters from **[Miqdad Badjuber's Anti Slop](https://github.com/miqdadbadjuber/anti-slop)**.

---

## 1. Repository Context & Architecture

**social-promo-bot** is an automated cross-platform social media marketing engine targeting X (formerly Twitter) and Threads:
- **Core Engine**: Python 3.10+, Playwright browser automation with isolated local persistent context profiles (`browser_profiles/`).
- **Data Layer**: Excel spreadsheet data queue (`promo_data.xlsx`) managed via `pandas` and `openpyxl`, with dynamic reply templates (`reply_templates.txt`).
- **Core Components**:
  - `main.py`: Interactive CLI dashboard, argument parsing, scheduler daemon, and task execution pipeline.
  - `config.py`: Global runtime constants, safety typing delays, DOM timeouts, and profile paths.
  - `data_manager.py`: Data access layer for spreadsheet queue extraction, schedule normalization, and status tracking.
  - `setup_accounts.py`: One-time interactive browser session initializer for local credential persistence.
  - `posters/`: Decoupled platform interaction handlers (`base_poster.py`, `x_poster.py`, `threads_poster.py`, `engagement_bot.py`).

---

## 2. Software Engineering Lifecycle

Every non-trivial code modification MUST follow the structured 6-phase engineering lifecycle:

```text
  DEFINE          PLAN           BUILD          VERIFY         REVIEW          SHIP
 ┌──────┐      ┌──────┐      ┌──────┐      ┌──────┐      ┌──────┐      ┌──────┐
 │ Idea │ ───▶ │ Spec │ ───▶ │ Code │ ───▶ │ Test │ ───▶ │  QA  │ ───▶ │  Go  │
 │Refine│      │  PRD │      │ Impl │      │Debug │      │ Gate │      │ Live │
 └──────┘      └──────┘      └──────┘      └──────┘      └──────┘      └──────┘
```

1. **DEFINE (`spec-driven-development`)**:
   - Establish formal specifications, boundary conditions, error handling, and platform constraints prior to code generation.
2. **PLAN (`planning-and-task-breakdown`)**:
   - Decompose work into discrete, atomic, and testable increments.
3. **BUILD (`incremental-implementation` + `test-driven-development`)**:
   - Deliver implementation in thin slices. Validate each step before moving forward.
4. **VERIFY (`debugging-and-error-recovery`)**:
   - Rigorously test execution pathways, browser timeout edge cases, selector fallback mechanisms, and concurrency.
5. **REVIEW (`code-review-and-quality`)**:
   - Audit diffs across 5 primary axes: correctness, architectural cleanliness, security (credentials/cookie handling), performance, and maintainability.
6. **SHIP (`shipping-and-launch`)**:
   - Ensure documentation is synchronized, spreadsheet data integrity is preserved, and launch scripts execute cleanly.

---

## 3. Anti-Slop Quality Standards

Agents are **STRICTLY PROHIBITED** from generating generic AI slop:

### A. Code Cleanliness & Comment Hygiene (`antislop-code`)
- **No Trivial Comments**: Delete comments that merely restate the code syntax (e.g. avoid `# loop over items` above `for item in items:`).
- **No Decorative ASCII Art / Banners**: Prohibit excessive boundary boxes (such as `#################`, `/* ================= */`, etc.).
- **Document the "Why"**: Comments must exclusively explain architectural rationale, platform-specific browser bug workarounds, or non-intuitive design assumptions.

### B. Promotional Copywriting & Templates (`antislop-copywriting`)
- **Zero AI Buzzwords**: Never employ clichés such as *"revolutionary"*, *"unlock your potential"*, *"game changer"*, or *"in today's fast-paced world"*.
- **No Emoji Cascades**: Avoid ungrounded emoji bullet points (e.g. repeated 🚀, 🔥, ⚡).
- **Honest & Direct Copy**: Compose promotional messages, reply templates (`reply_templates.txt`), and product captions in concise, natural, and human phrasing.

### C. UI & Visual Aesthetics (`antislop-ui`, `antislop-human`, `antislop-layoutmobile`)
- **Authentic Engineering**: Avoid generic AI visual tropes (identical purple-cyan gradients, purposeless floating cards, artificial metrics).
- **Human Usability & Accessibility**: Enforce readable contrast ratios, functional keyboard navigation, and explicit button states.

---

## 4. Customization Architecture & Skills Catalog

All agent capabilities reside within `.agents/`:

```text
.agents/
├── rules/
│   └── antislop.md                # Contextual anti-slop filter rule
├── skills/                        # 31 Progressive on-demand skills
│   ├── antislop/                  # Core 38 rules (R-01 to R-38) & delivery gate
│   ├── antislop-code/             # Comment hygiene filter
│   ├── antislop-copywriting/      # Human marketing copy guidelines
│   ├── antislop-human/            # Real-world accessibility & UX standards
│   ├── antislop-layoutmobile/     # Responsive layout & touch target standards
│   ├── antislop-ui/               # Visual layout filter
│   ├── spec-driven-development/   # Formal specification workflows
│   ├── planning-and-task-breakdown/
│   ├── incremental-implementation/
│   ├── test-driven-development/
│   ├── debugging-and-error-recovery/
│   ├── code-review-and-quality/
│   ├── code-simplification/
│   ├── security-and-hardening/
│   └── ... (31 skills total)
├── agents/                        # Specialized subagent personas
│   ├── code-reviewer.md
│   ├── security-auditor.md
│   ├── test-engineer.md
│   └── web-performance-auditor.md
└── references/                    # Shared engineering checklists
    ├── accessibility-checklist.md
    ├── definition-of-done.md
    ├── security-checklist.md
    ├── testing-patterns.md
    └── ...
```

---

## 5. Intent → Skill Routing Matrix

Agents should map incoming engineering tasks directly to specialized skills:

| Task / User Intent | Primary Skill Activated |
|:---|:---|
| New feature / modifying bot workflow | `spec-driven-development` &rarr; `planning-and-task-breakdown` &rarr; `incremental-implementation` |
| Error diagnosis / stuck browser / obsolete DOM selector | `debugging-and-error-recovery` |
| Writing social media copy / promo templates | `antislop-copywriting` + `antislop` |
| Code refactoring & cleanup | `code-simplification` + `antislop-code` + `refactoring-and-technical-debt` |
| Pre-commit / pre-merge code review | `code-review-and-quality` (persona: `code-reviewer`) |
| Credential, cookie, & session security audit | `security-and-hardening` (persona: `security-auditor`) |
| UI improvements / CLI styling | `frontend-ui-engineering` + `antislop-ui` + `antislop-human` |
| Execution speed & browser resource optimization | `performance-optimization` |
