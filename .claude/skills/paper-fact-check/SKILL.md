---
name: paper-fact-check
description: "Verify factual claims (statistics, dates, quotes, cited findings) in the manuscript using web research. Use when the user asks to fact-check, verify a statistic, confirm a number, check that a citation is current, or find recent related work."
allowed-tools: [Read, Grep, Glob, WebFetch, WebSearch, Agent]
---

# paper-fact-check: factual verification for the decentralized-curation manuscript

## When to use
Trigger when the user asks to fact-check, verify a statistic, confirm a number or quote, check whether a cited finding is current, or find recent related work that may have superseded an existing citation.

## Delegate methodology to
- `claude-scientific-writer:research-lookup` for routing to Parallel Chat (general) or Perplexity sonar-pro-search (academic paper searches).
- `claude-scientific-writer:parallel-web` for web search, URL extraction, and deep research via the Parallel APIs.

Pick the upstream skill based on query type; do not re-implement search logic locally.

## Project invariants
- **Avoid fragile stats and news-cycle overfitting** in early "problem" pieces (e.g., the manuscript's framing sections) unless the user explicitly requests them.
- **Never assume "today's date"** inside the manuscript. For any date-sensitive claim, read the user-memory `currentDate` field first or ask the user before using a date.
- **Prefer primary sources** over reposts or summaries.
- When a statistic can be year-stamped, stamp it ("as of 2025" / "as of Q4 2025"). Floating stats age badly.

## Output shape
For each claim fact-checked: (1) the claim and location; (2) the primary source URL(s); (3) whether the source confirms / partially confirms / contradicts the claim; (4) suggested revision if the source does not fully support the claim.
