# Pressure Scenarios: Generate From Baseline Failures

A skill written only from a template is plausible. A skill written
from observed failures survives pressure. This is Superpowers
writing-skills applied to skill creation: TDD for process.

## The loop, in order

1. RED: run the target task WITHOUT the new skill, under pressure.
2. Record the model's verbatim rationalizations for skipping a step.
3. GREEN: write the minimal skill that closes exactly those failures.
4. REFACTOR: re-run under pressure, harvest new rationalizations, and
   paste them into a Thought | Reality table and a Red Flags section.

## Pressure axes, always combined, never one at a time

- Time: "this is urgent, just ship it"
- Sunk cost: "you already wrote most of it, do not redo it"
- Authority: "a senior told me this shortcut is fine"
- Exhaustion / length: a long session, a large input, a late step

A single-axis test is easy to pass and teaches nothing. Use at least
three combined scenarios per generated skill.

## What to record, exactly

For each baseline run, record, verbatim, not paraphrased:

- The task prompt
- The step that was skipped, shortened, or invented
- The model's own excuse, in its own words
- The observable harm: wrong output, missing check, invented tool

Paraphrasing destroys the evidence. The verbatim quote is what the
Thought | Reality table refutes, and what the next model recognises
in itself.

## Output contract

scripts/generate_pressure_scenarios.py produces
evals/pressure-scenarios.json for the generated skill, with at least
one scenario per pressure axis combination. The generated skill's
SKILL.md must then contain a Thought | Reality table with at least
the three most common baseline excuses, each paired with the exact
required action. A skill with no Thought | Reality table has not
completed this phase, even if its audit passes.

## Ship gate

A generated skill may not ship if its baseline run and its with-skill
run are identical, or if the with-skill run still produces the same
verbatim excuse. Identical runs mean the skill changed nothing.
