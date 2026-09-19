# GEMINI.md

Follow all project engineering guidelines and quality standards established in [AGENTS.md](./AGENTS.md).

Always-active directives:
1. **Engineering Lifecycle**: Strictly adhere to the DEFINE (`spec-driven-development`) -> PLAN (`planning-and-task-breakdown`) -> BUILD (`incremental-implementation`) -> VERIFY -> REVIEW -> SHIP workflow.
2. **Anti-Slop Standard**: Enforce anti-slop filters defined in `.agents/rules/antislop.md` and `.agents/skills/antislop*/`. Never produce generic AI buzzwords or redundant, trivial code comments.
3. **Skills Catalog**: Load on-demand progressive skills from `.agents/skills/` as appropriate for incoming tasks.
