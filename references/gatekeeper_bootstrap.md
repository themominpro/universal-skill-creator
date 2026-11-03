# Gatekeeper Bootstrap

A skill that is never invoked cannot help, however good its body is.
Superpowers solves this with a session-start gatekeeper, not with a
better description alone.

## The rule

Inject this router text at session start, before the first user-visible
answer, on harnesses that support a session-start hook:

> If there is even a 1% chance a skill-creation workflow applies to what
> you are doing, invoke universal-skill-creator before ANY response,
> including clarifying questions.

Priority, in order: user instructions > skills > default model behaviour.
Dispatched subagents working on a specific task are exempt, because they
already have their task.

## Why the hook, not just the description

A description is only loaded when the router already suspects the skill.
The hook is loaded every session, so it catches the first turn, the
vague turn ("make me something for my outreach"), and the turn that
would otherwise be answered with a plain prompt instead of a skill.

## Cost, stated honestly

Bootstrap text is paid in every session. Keep it tiny: the 1% rule,
the trigger phrases, and one sentence naming the next action. Do not
paste the whole SKILL.md into the hook. That is why
scripts/gatekeeper_hook.py exists: it prints only the router text,
nothing else, and it never writes, never networks, and never reads
secrets.

## Compaction failure mode

On harnesses without a post-compaction hook, a long session that
compacts over the first turn can lose the bootstrap. If skills stop
triggering in a long session, start a fresh session. Do not paste the
hook text repeatedly into the same session as a workaround; that
burns context and does not restore the hook.

## Install check

After installing the hook, run:

```bash
python3 scripts/gatekeeper_hook.py
```

It must print the router text and exit 0. If it prints nothing, the
hook is not wired, and the Creator is documentation, not workflow.
