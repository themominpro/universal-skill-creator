# example-tool core guide

## The core loop

```
example-tool open <url>
example-tool snapshot -i
example-tool click @e3
example-tool snapshot -i
```

Refs are assigned fresh on every snapshot. They become stale the
moment the page changes. Always re-snapshot before your next
ref interaction.

## Waiting

Agents fail more often from bad waits than from bad selectors.
Prefer `example-tool wait @e1`, `example-tool wait --text`, or
`example-tool wait --url`. A bare millisecond wait is last resort.

## Commands

Use `example-tool skills get core` for the full command reference.
Do not guess flags. Load one reference at a time with
`example-tool skills get core --ref commands`.
