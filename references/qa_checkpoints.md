# QA Checkpoints: Ask at Every Stage, Not Only at the Start

Phase 2 triage alone is not enough when a wrong architecture, a
wrong workflow, or a wrong ship decision is expensive. These
checkpoints are mandatory. They do not replace Phase 2 triage,
they extend it to every decision that is hard to reverse.

## The rule for every checkpoint

Present a compact decision summary, at most 5 lines, then ask
at most 2 questions, each with a (Recommended) default and a
one-sentence trade-off. Record the checkpoint with
scripts/record_qa.py. Never ask more than 2 questions at one
checkpoint, never ask a question the workspace files already
answer, and never ask about implementation details that do not
change the outcome.

If the skill is low blast radius and reversible, presenting the
summary and proceeding on the recommended default is allowed,
but the summary and the assumed answers must still be recorded.
If the skill is commercial, destructive, or mutually exclusive
in architecture, wait for the user's reply at that checkpoint
before proceeding. Do not silently proceed past a high-blast
checkpoint.

## Checkpoint 1: After Phase 0, teardown and domain

Present: niche, top 2-3 competitors, their main loopholes and
strengths, the antidote, and the top 3 domain footguns.
Ask only if blocking: is the niche boundary right, is the
antidote the right one to build around?

## Checkpoint 2: After architecture, before drafting

Present: 6-tier structure, routing table rows, script list,
reference list, and what the skill will NOT do.
Ask only if blocking: is the routing table complete, is any
script missing or unnecessary?

## Checkpoint 3: After draft workflow, before gates

Present: workflow steps in order, decision tables, anti-
rationalization table entries, and example input/output.
Ask only if blocking: does any step miss a real-world edge
case, is any decision table wrong?

## Checkpoint 4: After gates, before packaging

Present: audit grade, security result, pressure excuses closed,
baseline pass rate and delta, render QA result.
Ask only if blocking: is any failed or waived gate acceptable,
is the baseline delta convincing?

## Checkpoint 5: Before ship, after trigger and bundle

Present: trigger positives and negatives, bundle contents,
gatekeeper status, and stub/router status if applicable.
Ask only if blocking: is this ready to ship, or must one gate
be re-run?

## What a checkpoint record must contain

Checkpoint name, decision summary, questions asked (0-2),
answers or assumed defaults, and whether the user confirmed
or the recommended default was used. A checkpoint with no
record is a checkpoint that did not happen, even if the chat
mentions it.
