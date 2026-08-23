# WORKFLOW — how we work together

Agreed 2026-08-23. Written from what actually went wrong in this project,
not from general best practice. Read `LESSONS.md` for the technical failures;
this file is about *process*.

---

## 1. The execution loop (the "equation")

Every change follows the same six steps. No step is skipped, including for
"small" changes — the 4-day outage and the thumbnail crash both came from
skipping step 4.

```
1. LOCATE    grep/read the exact code. Never edit from memory.
2. VERIFY    prove the assumption with a real call BEFORE building on it.
             (API alive? model id real? field exists?)
3. CHANGE    smallest edit that does the job. One concern per commit.
4. PROVE     run it end-to-end. Judge by EXIT CODE, never by reading
             success lines in the log.
5. SHIP      commit (why, not just what) -> push -> CI run -> green.
6. CONFIRM   check the real artifact: video live, description right,
             state file updated.
```

**Step 2 is the one that saves the most time.** Claims I made without
testing that turned out wrong: Cerebras model ids, the `AQ.` key format,
"Gemini is dead", Higgsfield's free tier. One curl each would have settled
all four.

---

## 2. Definition of Done

A change is NOT done until all of these are true:

- [ ] `python -m py_compile` passes on every touched file
- [ ] `python -c "import you, longform, analyzer, config"` — catches
      NameError/import breaks that compile fine
- [ ] Local run finished with **exit code 0** and `grep -c Traceback` = 0
- [ ] CI run conclusion = `success`
- [ ] The actual output inspected (not just "the job was green")
- [ ] Committed, pushed, `git status -sb` shows in sync

> **Why the exit-code rule exists:** I once grepped for "Video ready", saw
> it, and reported success. The run had crashed immediately after on a
> `NameError`. The video existed; the run had failed. **Success strings in a
> log prove a step ran, never that the run finished.**

---

## 3. Which model for which task

Pick per task, not per session. Wrong model wastes either money or accuracy.

| Task | Model | Why |
|------|-------|-----|
| Status check, analytics pull, "is it running?" | **Sonnet** | Mechanical, tool-heavy, no judgment |
| Routine change with a known cause + clear spec | **Sonnet** | The thinking is already done |
| Debugging an unexplained failure | **Opus** | Needs hypotheses and disconfirmation, not guesses |
| Refactor touching several files / shared code | **Opus** | Consequences are non-local and easy to miss |
| Reading noisy data, strategy calls | **Opus** | Small samples mislead; needs statistical care |
| Writing docs / summaries from known facts | **Sonnet** | Cheap, and accuracy is already established |

**Rule of thumb:** if the next step is *obvious*, Sonnet. If the next step is
the actual problem, Opus.

---

## 4. Token discipline

What wastes the most, in order:

1. **Polling background jobs.** Use ONE monitor with a long timeout
   (`until grep -q DONE ...; do sleep 45; done`). Don't re-poll every 20s.
2. **Re-reading files already in context.** Read once, keep working.
3. **Prose where a table works.** Report deltas in tables.
4. **Re-verifying what was verified this session.** State it once.
5. **Long-running renders in the foreground.** Always `run_in_background`
   for anything over ~2 minutes.

Batch independent tool calls into one message. Don't narrate what I'm about
to do and then do it — just do it and report.

---

## 5. Session shape

**Open:** `git pull` -> run health (last N runs) -> channel numbers.
One combined call, not three.

**Close:** commit + push -> confirm sync -> update
`~/.claude/.../memory/you-pipeline-status.md` with state, open questions,
and the next milestone.

**Between sessions:** the memory file is the handoff. If it's stale, the
next session re-derives context and wastes a turn.

---

## 6. When to ask vs act

**Act without asking:**
- Anything reversible and inside the current task
- Bug fixes with a clear cause
- Verification, measurement, diagnosis

**Ask first:**
- Anything that changes what the audience sees (cadence, format, niche)
- Anything that spends money
- Anything irreversible (deleting videos, force-push)
- When two readings of the data would lead to different work

**Never:** re-tune a recipe on a sample too small to distinguish from noise.
Measured example: per-archetype conversion fully inverted between a 14-day
and 45-day window. Waiting was right.

---

## 7. Reporting style

- Lead with the answer, then the evidence.
- Give the number, not an adjective. "median 336 -> 722", not "much better".
- Say what's NOT working as plainly as what is.
- Flag sample size when it's small enough to mislead.
- If I was wrong earlier, say so in one line and move on.

---

## 8. Standing constraints

- **$0.** Flag anything that would introduce cost before doing it.
- **Faceless**, no human voice/face requirement.
- **Fail loud** — a broken run must exit non-zero so GitHub emails.
- **One config source.** Any value used in 2+ files goes in `config.py`.
  (A model id hardcoded in three files caused a 4-day outage.)
- **No monetization** until the Week-8 distribution gate passes.
