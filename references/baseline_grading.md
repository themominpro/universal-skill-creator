# With-Skill vs Baseline Grading

This is the Anthropic skill-creator loop, made a hard gate instead
of an optional review. A generated skill must beat no skill, on the
same task, with evidence, or it does not ship.

## Sequence, in order

1. Write prompts first, assertions second, in parallel. Use 2-3
   realistic prompts for the generated skill's real job.
2. Spawn the with-skill run AND the baseline run in the same turn.
   Do not run them days apart, on different models, or with
   different prompts, and then compare the scores.
3. Draft assertions while the runs execute.
4. Capture timing immediately from completion notifications. That
   is the only chance to get it. Record it in timing.json.
5. Grade with agents/grader.md. The grader reads transcripts and
   outputs, grades each assertion, and writes grading.json.
6. Aggregate with scripts/grade_baseline.py into benchmark.json:
   pass_rate, time, tokens, mean plus/minus standard deviation,
   delta, with_skill first.
7. Human review gate: empty feedback means approval. Non-empty
   feedback means iterate into a new iteration folder, re-running
   baselines every time. Never reuse an old baseline score for a
   new version of the skill.

## Grader contract, exact

Each grading entry must have exactly three fields:

- text: the assertion, in full
- passed: true or false, never partial, never "mostly"
- evidence: a quoted excerpt from the transcript or output that
  proves the verdict

The grader must also write an eval_feedback block critiquing the
evals themselves, flagging any assertion a hallucinated document
would also pass. An eval that a hallucination passes is not an eval.

## Ship gate, numeric, not vibes

Ship only if ALL of these hold:

- with-skill pass_rate >= 80%
- with-skill pass_rate - baseline pass_rate > 0
- No regression: no assertion that passed at baseline fails
  with-skill, unless the human reviewer explicitly waives it in
  writing in feedback.json, with a reason
- grading.json passes scripts/grade_baseline.py with 0 contract
  violations

If any condition fails, the skill is not apex-tier, however clean
its audit score is. Record the benchmark in the generated skill's
evals/ folder, not only in chat.

## Blind comparison, for revisions

For a revision, use agents/comparator.md for a double-blind
comparison against the baseline: score instruction-following 1-10,
discourage ties, then unblind. The comparator must not know which
output used the skill until after scoring.
