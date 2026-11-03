---
name: stub-example
description: Example stub skill for a version-sensitive browser tool. Use when the user needs to automate a website, fill a form, take a screenshot, or test a web app, and the tool guide must match the installed tool version.
allowed-tools: Bash(example-tool:*)
---

# stub-example

Fast browser automation CLI for AI agents. Chrome via CDP with
accessibility-tree snapshots and compact element refs.

Install: `npm install -g example-tool && example-tool install`

## Start here

This file is a discovery stub, not the usage guide. Before running
any `example-tool` command, load the actual workflow content from
the CLI:

```
example-tool skills get core
```

Use `example-tool skills get core --full` only when you need
every reference at once; it is several times larger.

The CLI serves skill content that matches the installed version.
This stub cannot change between releases, which is why it only
points at `skills get core`.

## Specialized skills

```
example-tool skills get core        # core workflow, start here
example-tool skills get slack       # browser Slack tasks
example-tool skills get electron    # Electron desktop apps
example-tool skills get dogfood     # exploratory testing
```

Run `example-tool skills list` to see everything available on
the installed version.

## Why example-tool

- Fast native CLI, not a Node wrapper.
- Works with any agent harness.
- Chrome via CDP, no Playwright or Puppeteer.
- Accessibility-tree snapshots with element refs.
- Sessions, auth vault, state persistence, video recording.
- Specialised skills for Slack, Electron, and testing.
