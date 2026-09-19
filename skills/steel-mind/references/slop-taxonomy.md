# Slop Taxonomy - AI Output Anti-Patterns

A reference catalog for detecting and eliminating AI slop patterns.
Used by the steel-mind skill.

---

## Category 1 - Filler and Boilerplate

These patterns carry zero information. They exist because high-frequency
training tokens have high probability at sentence boundaries.

| Pattern | Example | Severity |
|---------|---------|---------|
| Stock greeting | "Hello! I'm happy to help you with that." | High - delete entirely |
| Affirmation opener | "Certainly!" / "Absolutely!" / "Of course!" | High - delete entirely |
| Sycophantic opener | "Great question!" / "That's a fascinating point!" | High - delete entirely |
| Transition filler | "Furthermore, ..." / "Moreover, ..." / "In addition, ..." | Medium - only keep if transition is genuinely needed |
| Vague qualifier | "In most cases" / "Generally speaking" / "Often" | Medium - replace with specific scope |
| Sign-off filler | "Feel free to ask if you have questions!" | Medium - delete entirely |
| Pre-emptive apology | "I'll do my best to help, but..." | High - delete entirely |

## Category 2 - Repetition and Circularity

| Pattern | Example | Fix |
|---------|---------|-----|
| Prompt echo | Repeating the user's full question before answering | Delete - start with the answer |
| Conceptual loop | "To answer this, we first need to answer this..." | Rewrite linearly |
| List inflation | Items 3-5 are rephrasings of items 1-2 | Remove duplicate items |
| Summary that repeats body | "In conclusion, X is good because A, B, C" after body already said A, B, C | Remove conclusion or make it additive |
| Introduction that previews | "I will now explain X, Y, and Z" before explaining X, Y, Z | Remove the preview, start explaining |

## Category 3 - Hallucination and Fabrication

The most dangerous slop category. Presents invented content as fact.

| Pattern | Example | Fix |
|---------|---------|-----|
| Phantom citation | "(Smith, 2021, Journal of AI Studies)" - no real paper | Remove or replace with "source unknown" |
| Invented statistic | "90% of developers prefer X (Source: Global Survey)" | Remove or qualify as estimate |
| Non-existent API | Calling a function that doesn't exist in the library | Verify in docs/source before asserting |
| Hallucinated file path | "The config is at /app/config/settings.php" without verification | Verify with a directory listing first |
| Mis-attributed quote | "Einstein said: '...'" (no record) | Remove or verify |
| Future-tense fabrication | "The next version will include X" without source | Qualify as speculation or remove |

## Category 4 - Over-Hedging

The opposite of hallucination - but equally useless. Drowns signal in noise.

| Pattern | Example | Fix |
|---------|---------|-----|
| Stacked modals | "It might possibly be able to potentially..." | Pick one or state directly |
| "I'm not sure, but" before a definitive claim | "I'm not sure, but PHP uses `->` for object access" | If you know it, state it |
| "According to some sources" | "According to some sources, this approach works" | Name the source or say "unverified" |
| Unnecessary caveat storm | 3+ caveats before a simple answer | State the answer, then add one relevant caveat |

## Category 5 - Formatting Abuse

Markdown used to create the appearance of structure without content.

| Pattern | Example | Fix |
|---------|---------|-----|
| Empty table cells | Table with blank cells | Fill or remove the table |
| One-line sections | `## Step 1\n\nDo X.` repeated 5 times | Use a numbered list or prose |
| Code fence around non-code | Prose wrapped in triple backticks | Remove fences |
| Heading hierarchy collapse | H2 > H3 > H4 for a 3-line section | Flatten to prose or a list |
| Bold everything | **Every** **single** **word** **bolded** | Bold only genuinely critical terms |

## Category 6 - Reasoning Shortcuts

Claims made without showing the work.

| Pattern | Fix |
|---------|-----|
| "Therefore, the answer is X" (no derivation shown) | Show the intermediate steps |
| "Chain-of-thought" that terminates early | Complete all steps including the final conclusion |
| One-sentence justification for a complex claim | Expand the reasoning or qualify the claim |
| "This is the best approach" without comparison | State why vs what alternatives |

---

## Quick Detection (3-flag Rule)

If 3 or more of these are present in a response, the response needs a rewrite:

- [ ] First sentence contains zero substantive information
- [ ] 2+ generic transition phrases
- [ ] Any claim without traceable grounding
- [ ] Identical phrasing appears twice within 100 tokens
- [ ] A heading exists with fewer than 3 lines of content under it
- [ ] An apology or hedge appears before the main content
