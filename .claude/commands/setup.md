# /setup — Onboarding

Walks new users through everything needed to start using CareerScout: resume, context files, writing voice, and the job feed. Each step can be skipped and done later.

---

## Protocol

### Step 1 — Welcome

Say:

> "Welcome to CareerScout. Let's get you set up — this takes about 10-15 minutes depending on how much you want to configure now.
>
> We'll go through:
> 1. Your resume (required — everything else builds from this)
> 2. Your context files (copying templates you can fill in over time)
> 3. Your writing voice (optional — makes cover letters and tailored bullets significantly more accurate)
> 4. Your job feed (optional — daily scored shortlist of roles worth applying to)
>
> You can skip 3 and 4 now and run `/voice-setup` or `/feed-setup` any time.
>
> **To start: paste your resume below.** Any format is fine — plain text, copied from a PDF, or a Word doc."

---

### Step 2 — Save the resume

Wait for the user to paste their resume. Once received:

1. Save the full content to `context/resume.md` with this header:
   ```
   # Resume
   
   [pasted content]
   ```
2. Confirm: "Resume saved to `context/resume.md`."

If the user asks to skip or says they don't have one ready, say: "No problem — paste it in when you're ready and I'll save it then. Without it I can't run assessments or tailor bullets, but you can still use `/track` to manage applications."

---

### Step 3 — Copy context files

Copy the example files to create the user's context files. For each file below, read the `.example.md` version and write the same content to the non-example path (if it doesn't already exist — don't overwrite):

| Source | Destination |
|--------|-------------|
| `context/profile.example.md` | `context/profile.md` |
| `context/bank.example.md` | `context/bank.md` |
| `context/state.example.md` | `context/state.md` |
| `context/sources.example.md` | `context/sources.md` |
| `context/differentiators.example.md` | `context/differentiators.md` |

After copying, say:

> "Context files created. You don't need to fill these in now — they populate automatically as you use the agent. The one worth glancing at is `context/profile.md`, which is where you can add context that isn't on your resume: comp targets, location preferences, things you want to avoid, and any background on specific roles."

---

### Step 4 — Voice setup

Ask:

> "Next: your writing voice. This calibrates how I write cover letters and tailored bullets — the output sounds like you, not like a template. It takes about 5 minutes.
>
> Want to do this now? (You can also run `/voice-setup` any time.)"

- If yes → run the full `/voice-setup` protocol inline
- If no / skip → note it and move on: "Skipped for now — run `/voice-setup` before your first cover letter."

---

### Step 5 — Feed setup

Ask:

> "Last step: the job feed. This scrapes LinkedIn, Indeed, and direct ATS endpoints daily and scores roles against your criteria — so instead of manually searching, you get a shortlist each morning.
>
> It requires Python 3 and a one-time install. Want to set it up now? (You can also run `/feed-setup` any time.)"

- If yes → run the full `/feed-setup` protocol inline
- If no / skip → note it and move on: "Skipped for now — run `/feed-setup` when you're ready."

---

### Step 6 — Done

Close with a summary of what was completed and a clear first action:

> "You're set up. Here's where things stand:
>
> - ✓ Resume saved
> - ✓ Context files created
> - [✓ / —] Writing voice [calibrated / skipped]
> - [✓ / —] Job feed [configured / skipped]
>
> **Next:** [if feed configured → "Run `python3 feed-agent/fetch.py` then `/feed` to get your first scored shortlist."] [if feed skipped → "Paste a job description and I'll run `/assess` to get started."]"
