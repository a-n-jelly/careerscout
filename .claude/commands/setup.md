# /setup — Onboarding

Walks new users through everything needed to start using CareerScout in one flow. Each step can be skipped and done later.

---

## Protocol

### Step 1 — Welcome

Say:

> "Welcome to CareerScout. Let's get you set up — this takes about 10-15 minutes depending on how much you want to configure now.
>
> We'll go through:
> 1. Your resume (required — everything else builds from this)
> 2. A few quick questions to set up your context files
> 3. Your writing voice (optional — makes cover letters and tailored bullets significantly more accurate)
> 4. Your job feed (optional — daily scored shortlist of roles worth applying to)
>
> You can skip 3 and 4 now and run `/voice-setup` or `/feed-setup` any time.
>
> **To start: paste your resume below.** Any format is fine — plain text, copied from a PDF, or a Word doc."

---

### Step 2 — Save the resume

Wait for the user to paste their resume. Once received:

1. Save the full content to `context/resume.md`:
   ```
   # Resume

   [pasted content]
   ```
2. Confirm: "Resume saved to `context/resume.md`."

If the user asks to skip or says they don't have one ready: "No problem — paste it when you're ready. Without it I can't run assessments or tailor bullets, but you can still use `/track` to manage applications."

---

### Step 3 — Populate context files

Ask the following questions in a single pass — present them all at once, not one at a time:

> "A few quick questions to set up your profile. Leave anything blank — you can fill it in later.
>
> **Your name** (for sign-offs):
>
> **Target base salary** (e.g. $150k–$180k):
>
> **Location / remote preference** (e.g. Seattle, open to remote, hybrid OK):
>
> **Must-haves** — things a role needs for you to consider it (e.g. equity, consumer product, early-stage):
>
> **Deal-breakers** — things that rule a role out immediately (e.g. pure enterprise sales, no sponsorship available, travel-heavy):
>
> **Anything about your background worth flagging** — career gaps, transitions, things recruiters might question, how you'd frame them:"

Once the user responds, use their answers to create the following files. **Delete the corresponding example file after creating each one.**

---

#### `context/profile.md`

Write with the user's answers filled in. Use this structure:

```markdown
> **Purpose:** The context behind your resume — things that are true but don't fit in a bullet. The agent reads this alongside `resume.md` when tailoring or writing cover letters. Add to it over time as you develop new framings, stories, or positioning.

# Profile & Off-Resume Context

---

## Who You Are (Positioning)

[Leave blank — will build up as you use /assess and /tailor.]

---

## Role-by-Role Context

[Leave blank — add interview stories and real-detail notes here as you prep for roles.]

---

## Career Gaps or Transitions

[User's answer, or leave blank if not provided.]

---

## Compensation & Preferences

**Target base:** [user's answer, or —]
**Location preference:** [user's answer, or —]
**Must-haves:** [user's answer, or —]
**Deal-breakers:** [user's answer, or —]
```

Then delete `context/profile.example.md`.

---

#### `context/bank.md`

Write with the user's name filled in for the sign-off. Everything else stays as the template default — voice-setup will populate the style section, and Q&A fills in over time.

```markdown
> **Purpose:** Your cover letter style guide and reusable talking points. The agent reads this before writing any cover letter or email.

# Bank — Cover Letter Points, Style & Q&A

---

## Cover Letter Style

- **Opening:** One short paragraph. Name the role and team. Connect your background to the company's mission using their own language where possible.
- **Body:** 2–4 bold headers drawn from the JD's key themes. Each is a short prose paragraph (3–5 sentences) — no bullets. Lead with context, follow with impact.
- **Closing:** One sentence tied to the specific team or product. No "I look forward to hearing from you."
- **Sign-off:** `Kind Regards, / [user's name, or "Your Name" if not provided]`

---

## Core Points

[Leave blank — will build up as you use /assess and /coverletter.]

---

## What to Avoid

[Leave blank — add framing or tone you want to avoid as you learn what doesn't land.]

---

## Q&A Bank

| Question | Answer |
|----------|--------|
| Why are you leaving your current/last role? | |
| Why this company? | |
| What's your biggest weakness? | |
| Salary expectations? | |
```

Then delete `context/bank.example.md`.

---

#### `context/state.md`

Write a clean empty pipeline using the user's name in the header:

```markdown
> **Purpose:** Your live application pipeline. The agent reads this at the start of every session and updates it automatically. Use `/track` and `/update` instead of editing directly.

# Application State — [user's name, or "Your Name"]
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

Then delete `context/state.example.md`.

---

#### `context/sources.md` and `context/differentiators.md`

Copy these from the example files without modification — `/feed-setup` will populate them properly.

Read `context/sources.example.md` → write to `context/sources.md`, then delete `context/sources.example.md`.
Read `context/differentiators.example.md` → write to `context/differentiators.md`, then delete `context/differentiators.example.md`.

---

After all files are created, confirm:

> "Context files set up. Your profile, pipeline, and cover letter bank are ready. They'll fill in automatically as you use the agent — you don't need to edit them directly."

---

### Step 4 — Voice setup

Ask:

> "Next: your writing voice. This calibrates how I write cover letters and tailored bullets so the output sounds like you, not a template. It takes about 5 minutes.
>
> Want to do this now? (You can also run `/voice-setup` any time.)"

- If yes → run the full `/voice-setup` protocol inline
- If no / skip → "Skipped — run `/voice-setup` before your first cover letter."

---

### Step 5 — Feed setup

Ask:

> "Last step: the job feed. This scrapes LinkedIn, Indeed, and direct ATS endpoints daily and scores roles against your criteria — so instead of searching manually, you get a shortlist each morning.
>
> It requires Python 3 and a one-time install. Want to set it up now? (You can also run `/feed-setup` any time.)"

- If yes → run the full `/feed-setup` protocol inline
- If no / skip → "Skipped — run `/feed-setup` when you're ready."

---

### Step 6 — Done

> "You're set up. Here's where things stand:
>
> - ✓ Resume saved
> - ✓ Context files created
> - [✓ Writing voice calibrated / — Skipped: run `/voice-setup`]
> - [✓ Job feed configured / — Skipped: run `/feed-setup`]
>
> **Next:** [if feed configured → "Run `python3 feed-agent/fetch.py` then `/feed` to get your first scored shortlist."] [if feed skipped → "Paste a job description and I'll run `/assess` to get started."]"
