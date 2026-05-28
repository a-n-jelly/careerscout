# Application Answer Examples

Approved writing samples for application questions. Use these as voice references when drafting — match tone, rhythm, and structure before applying style rules.

---

## Example 1: Describe an agentic AI product or feature you shipped
*(ApartmentIQ / MavenAI, April 2026 — used in place of cover letter)*

Little Places started as a personal problem. Finding child-friendly venues in Seattle as a parent is genuinely hard, and I kept hitting the same wall. Other parents were asking the same questions in forums, and after speaking to a number of them, it became clear that I wasn't alone with this problem.

So I built it. Scraped and structured the venue database, designed the experience (and redesigned it, and redesigned it again), and I'm managing the whole thing solo. Parents search in natural language, and an AI agent queries live data sources (venues, events, weather) to return grounded answers rather than whatever the model thinks it knows.

Being both the PM and the user is harder than it sounds when it's personal. I ended up building a whole Claude OS to compensate: learned what worked, what burned tokens, where I needed guardrails. Honestly I've spent more time refining that than actually building, but my work is getting faster and more efficient.

The biggest call was on data quality. When the venue data was thin, agent responses were plausible but untrustworthy. Worse than no answer at all. So I flipped to map-first: the map shows verified data directly, the agent handles queries where the data can actually support it. It earns its place rather than being assumed to work.

I've started looking into evals, but the reality is they're only useful if the data behind them is good. Until the venue data has enough depth for the agent to give genuinely helpful answers, evals can't tell me whether it's actually getting it right. So that's the dependency I'm working on first.

None of it would have been possible at this pace without AI. Claude Code was my primary dev tool throughout, alongside Anthropic API, Gemini, React/Vite, Supabase, and Mapbox.

Still building toward MVP, a few key decisions ahead of me, but it's live and it's public on GitHub.

---

## What makes this work

- Opens with the personal problem, not the product
- Validation is specific (forums, actual conversations) not vague ("I realised others had this problem")
- Short sentences land the key points; longer ones carry context
- Honest about what's hard (solo backlog, evals not ready) without it reading as a weakness
- Technical detail is specific but never leads — it follows the product thinking
- Ends with forward momentum, not a summary
