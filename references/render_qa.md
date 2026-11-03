# Render QA: Three Gates, With a Stop Rule

Prose claims are not proof. Document skills prove output by
rendering and looking, not by re-reading their own instructions.
Apply the same discipline to anything a generated skill produces.

## The three gates, in order

1. Content QA: search the output for lorem, unfinished-marker
   words, and invented names, tools, or prices. Any hit fails.
   The exact banned list is in scripts/render_qa.py.
2. File QA: validate the output file against its schema or
   template, and, for template-derived work, compare against
   the original with a baseline flag, the equivalent of
   --original in the document skills. A file that cannot be
   opened, parsed, or validated fails, even if it looks right.
3. Visual QA, when the output is visual or a document: render
   it to images or PDF and inspect every page or slide fresh,
   overflow first. Do not inspect only the first page.

## Stop rule

Fix, re-render only what changed, stop. Do not re-render the
whole output after every small fix, and do not stop after the
first clean page. A gate that is re-run on stale output is not
a gate.

## Traps to name in the generated skill itself

Name the trap, do not just hope the agent avoids it. Examples
from the document skills, adapted generally:

- A green validation proves a file evaluates or parses, not
  that it is right.
- An exit code of 0 with errors in the JSON output is still a
  failure. Check the output body, not only the exit code.
- A renderer, font, or tool version can change the result.
  Record the tool and version used for the QA render.

scripts/render_qa.py implements gates 1 and 2 deterministically:
placeholder scan, schema/file existence check, and a JSON
report with a PASS/FAIL per gate. Visual inspection remains a
human step, and the report must say so, never claim a visual
pass that no one performed.
