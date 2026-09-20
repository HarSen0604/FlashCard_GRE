# Verification record

The tests run in isolated temporary databases. The delivered database contains the original source archive and edited flashcards; study progress is reset after verification.

## Backend and content checks

`.venv/bin/python -m pytest tests -q`: **48 passed in 1.46s** on 2026-09-21.

Covered:

- Random sampling without duplicates; input validation including zero, negative, fractional, non-numeric, excessively large, and malformed requests.
- First encounters use a persisted teaching presentation that cannot be rated, does not create an event, and survives restart; existing active batches migrate without losing positive streak state.
- Later learning cards and all revision cards use recall presentations. Forgetting returns an active word to teaching, while undo restores the prior recall presentation.
- One active batch; batch persistence across application restart and multiple days.
- Three consecutive successes, reset on forgetting, and a final Easy response required for readiness.
- Intervening cards and the server-enforced 30-second fallback for a singleton/last word.
- Atomic graduation of the whole batch; a ready word remains outside revision while another word is unfinished.
- Revision during an active batch without changing initial-learning progress.
- FSRS due dates, forgotten-word relearning, early reviews, and separate learning/revision counts.
- Rating requires reveal; duplicate and concurrent submissions count only once; stale tokens are rejected.
- Local access requires both a loopback peer and local hostname. Tailscale Serve access requires a loopback proxy, `.ts.net` hostname, and authenticated Tailscale identity; missing/spoofed identities, direct LAN requests, and optional-login mismatches are rejected.
- Undo restores state, including whole-batch graduation and revision schedules/history.
- No new words after exhaustion; library search and confidence/due filters.
- SQLite backup integrity and inclusion of progress.
- All 995 original rows and all 6,965 original fields checked against the archived HTML, plus a byte-level archive hash check.
- Every original definition number accounted for in a display sense; every display sense has an example; relation lists have at most three distinct entries.
- Every example is at most 27 words; no non-verb gets generated tenses; irregular and inflected headwords are checked.
- GRE distinctions such as qualified, sanction, abridge, grouse, and secrete are retained.
- Startup and a study action using only a SQLite copy in a separate directory, without HTML or preparation files there.

## Browser checks

`.venv/bin/python tests/browser_check.py`: **passed** on 2026-09-21 using the installed Google Chrome. It launches a temporary local Flask server and headless browser.

The real user journey covers batch creation, persisted teaching after refresh/resume, primary meaning and single highlighted example, teaching continuation without ratings, recall with hint show/hide, full reveal without the hint, complete back content, per-card and reload hint reset, original-source inspection, rating, undo, completing three words through three recall rounds, graduation, early revision, and filtering learned words.

Every one of the 995 cards is rendered on both sides at 1440×1000, 1280×800, 768×1024, and 390×844. Checks detect horizontal card/page overflow and card text below 16 CSS pixels. Desktop/laptop fronts also check that the reveal button is within the viewport. Long backs are intentionally scrollable. Reports include scroll counts, JavaScript errors, and external network requests.

Representative desktop, laptop, and narrow-screen screenshots are saved alongside the JSON results. The teaching front, recall back, scrollable mobile back, and laptop back were visually inspected in this run.

## Scope

This verifies behavior and layout in the installed Google Chrome on macOS. It is not an exhaustive guarantee for every browser, operating system, or future database edit. Semantic grouping includes model-assisted and editorial review; automated coverage confirms that source definitions remain represented, rather than certifying dictionary accuracy by a numerical similarity score. The original archive remains available for comparison.

The Chrome report recorded no JavaScript errors or external network requests. Both test commands used isolated temporary databases; the personal runtime database was not opened, reset, or edited.
