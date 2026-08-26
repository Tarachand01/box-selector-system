# AI Usage Disclosure

## 1. AI tool(s) used

Claude (Anthropic), used through the Claude.ai chat interface.

## 2. What I did myself vs. what I used AI for

I wrote the initial implementation myself first — the `Product`, `Box`,
`Order`, and `OrderItem` models, the `select_box()` algorithm in
`boxes/services.py`, and the `/api/recommend-box/` endpoint. After I
had a working draft, I used Claude for three things:

- Researching Django and Django REST Framework concepts and patterns
  I wasn't fully sure about (e.g. serializer validation patterns,
  how DRF handles nested/optional input fields).
- Reviewing and improving code I had already written — going through
  my draft of `services.py` and the views/serializers and suggesting
  refactors, cleanup, or edge cases I might have missed.
- Writing and checking test cases against my implementation, to make
  sure the test suite actually exercised the behavior I intended
  (rotation, quantity scaling, tie-breaking, error paths).

## 3. Prompts given (representative, not verbatim)

1. Questions about specific DRF concepts and patterns while I was
   implementing the serializers and endpoint.
2. "Here's my `select_box()` implementation — can you review it and
   point out anything that looks wrong or could be cleaner?"
3. "Can you help me write/check test cases for this — am I missing
   any edge cases?"

## 4. What output was accepted

- Some refactoring suggestions for `select_box()` and the
  serializers, applied on top of my original implementation.
- Test cases suggested to cover edge cases I hadn't originally
  written for (e.g. tie-breaking on equal cost, item too large vs.
  too heavy as distinct failure paths).
- Clarification on a couple of DRF patterns that I then implemented
  myself.

## 5. What output was rejected or modified

- Not every suggested refactor was used as-is — some were adapted to
  fit the structure I already had rather than adopted wholesale.
- [Add specifics here: any suggestion you didn't take, or changed
  before using, so this section reflects your actual judgment calls.]
- Per the assignment brief, AI was not used for the exported chat
  transcript or the personal "what I learned" reflection — those were
  produced independently.

## 6. Mistakes the AI made

[Fill this in honestly — e.g. a review suggestion that turned out to
be wrong for your actual model structure, a test case that assumed
behavior your code didn't have, etc. If you genuinely didn't catch
any mistakes, say so, but it's worth double-checking review
suggestions against your own code before submitting.]

## 7. How the final code was verified

- `python manage.py makemigrations` and `python manage.py migrate`
  were run to confirm the models produce valid migrations.
- `python manage.py test boxes -v 2` was run, executing all 17 tests.
  Full output is in `TEST_OUTPUT.md`.
- I reviewed the suggested refactors and test cases against my own
  understanding of the algorithm before accepting them, rather than
  applying them automatically.
