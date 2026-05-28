# /setup — Onboarding

Guided onboarding for new users. Warm, coach-like tone throughout — this is their first experience with the agent. One flow, each step skippable.

---

## Protocol

### Step 1 — Welcome

Say:

> "Hey, welcome to CareerScout! I'm going to help you get set up so we can hit the ground running together.
>
> We'll go through four things:
> 1. Your resume — the foundation for everything
> 2. A few quick questions to personalise your profile
> 3. Your writing voice — so cover letters actually sound like you
> 4. The job feed — a daily scored shortlist so you're not manually searching
>
> Steps 3 and 4 are optional — you can skip them now and come back any time. Let's start.
>
> **Paste your resume below.** Any format works — plain text, copied from a PDF, whatever you've got."

---

### Step 2 — Save the resume

Wait for the user to paste their resume. Once received:

1. Save to `context/resume.md`:
   ```
   # Resume

   [pasted content]
   ```
2. Scan the resume and extract what you can: **full name**, **current or most recent location**, **current comp or comp signals** (if mentioned), **seniority level**.

3. Confirm warmly:
   > "Got it — resume saved. I can already see a lot to work with here."

If the user asks to skip: "No problem — you can paste it any time. A few things won't work without it (assessments, tailored bullets) but you can still track applications."

---

### Step 3 — Personalise the profile

Use what you extracted from the resume to pre-fill what you can. Only ask for things you couldn't determine.

Use the **AskUserQuestion tool** to ask in structured form. Ask all questions in a single tool call — do not ask one at a time.

Questions to include (skip any already known from the resume):

- **Target base salary** — offer 3-4 banded options + Other (e.g. Under $120k / $120k–$150k / $150k–$180k / $180k+ / Other)
- **Work setup preference** — Fully remote / Hybrid (few days/week) / Open to on-site / Flexible / Other
- **Must-haves** — things a role needs for you to seriously consider it (free text via Other)
- **Deal-breakers** — things that rule a role out (free text via Other)
- **Anything about your background to get ahead of** — gaps, transitions, short tenures, and how you'd frame them (free text via Other — optional, can skip)

After collecting answers:

**Create `context/profile.md`** with the structure below, filling in the user's answers and anything pre-filled from the resume. Then **delete `context/profile.example.md`**.

```markdown
> **Purpose:** The context behind your resume — things that are true but don't fit in a bullet. The agent reads this alongside `resume.md` when tailoring or writing cover letters.

# Profile & Off-Resume Context

---

## Who You Are (Positioning)

[Leave blank — builds up as you use /assess and /tailor.]

---

## Role-by-Role Context

[Leave blank — add interview stories and real-detail notes here as you prep for specific roles.]

---

## Career Gaps or Transitions

[User's answer, or blank if not provided.]

---

## Compensation & Preferences

**Target base:** [answer]
**Work setup:** [answer]
**Must-haves:** [answer, or —]
**Deal-breakers:** [answer, or —]
```

**Create `context/bank.md`** using the name extracted from the resume for the sign-off. Then **delete `context/bank.example.md`**.

```markdown
> **Purpose:** Your cover letter style guide and reusable talking points. The agent reads this before writing any cover letter or email.

# Bank — Cover Letter Points, Style & Q&A

---

## Cover Letter Style

- **Opening:** One short paragraph. Name the role and team. Connect your background to the company's mission using their own language where possible.
- **Body:** 2–4 bold headers drawn from the JD's key themes. Each is a short prose paragraph (3–5 sentences) — no bullets. Lead with context, follow with impact.
- **Closing:** One sentence tied to the specific team or product. No "I look forward to hearing from you."
- **Sign-off:** `Kind Regards, / [name from resume]`

---

## Core Points

[Builds up as you use /assess and /coverletter.]

---

## What to Avoid

[Builds up as you use the agent.]

---

## Q&A Bank

| Question | Answer |
|----------|--------|
| Why are you leaving your current/last role? | |
| Why this company? | |
| What's your biggest weakness? | |
| Salary expectations? | |
```

**Create `context/state.md`** using the name from the resume. Then **delete `context/state.example.md`**.

```markdown
> **Purpose:** Your live application pipeline. Updated automatically — use `/track` and `/update` instead of editing directly.

# Application State — [name from resume]
Last updated: [today's date]

---

## Pipeline Summary

| Company | Role | Status | Stage | Last Updated |
|---------|------|--------|-------|--------------|

---

## Active Applications

[None yet.]

---

## Closed

| Company | Role | Outcome | Date | Notes |
|---------|------|---------|------|-------|
```

**Create `context/sources.md`** and **`context/differentiators.md`** by copying from the example files without modification — `/feed-setup` will populate these properly. Then **delete both example files**.

Confirm:
> "Profile set up. Your pipeline and cover letter bank are ready too — they'll fill in as you go, you won't need to touch them directly."

---

### Step 4 — Writing voice

Use the **AskUserQuestion tool**:

- Question: "Want to calibrate your writing voice now? It takes about 5 minutes — you paste a few things you've written and I'll build a style profile from them. Every cover letter and tailored bullet will sound like you, not a template."
- Options: **Yes, let's do it** / **Skip for now**

- If yes → run the full `/voice-setup` protocol inline
- If skip → "No problem — run `/voice-setup` before your first cover letter and I'll pick it up then."

---

### Step 5 — Job feed

Use the **AskUserQuestion tool**:

- Question: "Want to set up the job feed? It scrapes LinkedIn, Indeed, and company ATS pages daily and scores roles against your criteria — so instead of searching, you get a shortlist each morning. It needs Python 3 installed."
- Options: **Yes, set it up** / **Skip for now**

- If yes → run the full `/feed-setup` protocol inline
- If skip → "Got it — run `/feed-setup` whenever you're ready."

---

### Step 6 — Done

Close warmly with a clear next step:

> "You're all set! Here's where we landed:
>
> - ✓ Resume saved
> - ✓ Profile and context files created
> - [✓ Writing voice calibrated / — Voice setup: run `/voice-setup` when ready]
> - [✓ Job feed configured / — Feed setup: run `/feed-setup` when ready]
>
> [If feed configured:] "Run `python3 feed-agent/fetch.py` in your terminal, then come back and type `/feed` — I'll score today's roles and give you a shortlist."
>
> [If feed skipped:] "When you've got a role in mind, paste the job description and I'll run `/assess` — fit score, what lands, what might concern a recruiter, and a suggested angle for the cover letter."
>
> Good luck — let's find you something great."
