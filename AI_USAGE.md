# AI Usage Disclosure

## 1. AI tool(s) used

Claude (Anthropic), used through the Claude.ai chat interface with its
code-execution/file-creation tool.

## 2. Prompts given

The relevant prompts in this session were, in effect:

1. "do the whole thing, and give me all the files that they asked
   for" — following an earlier message where the assignment brief
   (a Word document, `Assignment_-_Python_Django_Developer.docx`) was
   uploaded and its requirements were read out.

No further back-and-forth prompts were needed before Claude produced
a first complete version of the models, algorithm, API, and tests —
this file documents what that single generation pass produced and how
it was checked, not a long iterative dialogue.

## 3. What output was accepted

- The overall project structure: a `boxes` Django app with
  `Product`, `Box`, `Order`, `OrderItem` models.
- The core `select_box()` algorithm in `boxes/services.py`, including
  the fit-with-rotation check (sort both item and box dimensions
  ascending, compare pairwise), the combined-volume check, the weight
  check, and cheapest-cost tie-broken-by-size selection.
- The DRF serializers and the `/api/recommend-box/` endpoint,
  including the design choice to accept either an existing
  `product_id` or an inline one-off item description.
- The full test suite (17 tests) covering the algorithm directly and
  through the API.
- The README's description of the algorithm and its limitations.

## 4. What output was rejected or modified

- The assignment brief itself said not to use AI for two specific
  deliverables: the exported chat transcript and the personal "what
  did you learn" reflection. Claude did not generate these, and
  flagged this explicitly rather than attempting a workaround —
  those two files must still be produced independently.
- The initial framing considered a full 3D bin-packing solver, but
  that was deliberately scaled back to a volume-sum + per-item
  rotation-fit heuristic, since true 3D packing is a much larger
  problem than this assignment calls for. This trade-off is called
  out explicitly in the README as a known limitation rather than
  silently glossed over.

## 5. Mistakes the AI made

- None were caught in this pass that required a rewrite — the test
  suite was run immediately after code generation (see below) and
  passed on the first run. If issues are found during your own
  review, add them here along with how they were fixed, since that
  record is part of what this file is meant to capture.

## 6. How the final code was verified

- `python manage.py makemigrations` and `python manage.py migrate`
  were run to confirm the models are internally consistent and
  produce valid migrations.
- `python manage.py test boxes -v 2` was run, executing all 17 tests
  (9 pure-algorithm unit tests, 2 model-integration tests, 6 API
  integration tests hitting `/api/recommend-box/` through Django's
  test client). All 17 passed. Full output is in `TEST_OUTPUT.md`.
- The tests were written to include edge cases likely to expose bugs
  in a naive implementation: rotation-dependent fit, quantity
  multiplying both weight and volume, cost ties, and both
  "too heavy" and "too large" rejection paths.

**You should still read through the code yourself before submitting**
— re-run the tests locally, skim `services.py` in particular since
it's the core logic, and note in this file anything you'd have done
differently or any issue you find, as the assignment expects your own
verification on top of this record.
