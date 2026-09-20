# Wordwell — local GRE flashcards

A single-user Flask application with 995 cards, offline study, saved learning batches, and FSRS revision scheduling. All runtime data is in `data/flashcards.sqlite3`. The original HTML is **not required to run the app**.

## Start

Double-click `run.command` in Finder, or run:

```sh
cd FlashCard_GRE
.venv/bin/python app.py
```

Open **http://127.0.0.1:5055** in your browser. Stop with Ctrl+C. If the port is occupied, use `.venv/bin/python app.py --port 5057` and open that port instead. You do not need to activate the virtual environment when using these commands. The app listens only on the local laptop; no account, credentials, API key, or internet connection is needed for local study.

## Private phone access with Tailscale

Wordwell can remain bound to localhost while [Tailscale Serve](https://tailscale.com/docs/features/tailscale-serve) provides private HTTPS access to authenticated devices in your tailnet. Install and sign in to Tailscale on this Mac and the phone, start Wordwell normally, then run:

```sh
tailscale serve --bg 5055
tailscale serve status
```

Open the reported `https://…ts.net` URL on the phone while Tailscale is connected. The laptop must remain powered on, awake, connected, and running Wordwell. To stop sharing Wordwell, run `tailscale serve 5055 off` (or `tailscale serve reset` to remove all Serve configuration).

Tailscale Serve removes spoofed identity headers and supplies the authenticated `Tailscale-User-Login` header to the localhost backend. Wordwell accepts a `.ts.net` hostname only when that header arrives from a loopback proxy. For an extra account-level restriction, set the login used on the phone before starting Wordwell:

```sh
export WORDWELL_TAILSCALE_LOGIN='you@example.com'
.venv/bin/python app.py
```

Do not use Tailscale Funnel or router port forwarding for this application. Funnel is public internet exposure; Wordwell is designed for one user and does not have a separate password screen.

For a fresh installation on another computer (Python 3.10+), clone this repository, then create the environment:

```sh
git clone https://github.com/HarSen0604/FlashCard_GRE.git
cd FlashCard_GRE
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python app.py
```

Do not copy a virtual environment between computers. Recreate it with the commands above.

## How to study

1. Enter the number of **new words in this batch**. Sampling is random without replacement.
2. On a word's first encounter, read its primary plain meaning and one complete representative example. Continue to the full answer to see every retained meaning and example. This teaching exposure is not a recall attempt and cannot increase the streak.
3. Later learning repetitions ask you to recall the meaning without showing it. You may open **Show contextual hint** to see one complete example with the word or its inflection highlighted; the hint never reveals the definition, flips the card, or changes progress. Reveal the full answer with or without using the hint.
4. Rate actual recall only after revealing the complete answer:
   - **I do not remember:** reset the word's consecutive-success streak to zero and repeat sooner.
   - **Remembered, needs revision:** add one success; repeat later.
   - **Easy to remember:** add one success; mark ready if the streak is at least three.
5. A successful third response of “needs revision” does **not** graduate the word; it remains until an Easy response. A later failure resets the streak even when it had reached three and returns the word to a teaching presentation before recall resumes.
6. Teaching exposures and repeats are separated by another card whenever possible. Forgotten words receive a shorter queue delay (1 turn vs 3 for remembered and 5 for Easy); unseen words retain their randomized positions. If only one unfinished word remains, the server requires a 30-second gap instead. Reloading cannot bypass the gap.
7. Ready words stop repeating, but the **entire batch** stays in initial learning until every word is ready. Then all words move into **Already gone through** in one transaction.
8. Closing the browser or restarting the app preserves your exact batch and progress. Finish it before starting another new batch. Revision remains available meanwhile.

Learning is not a guarantee of long-term mastery. Use the subsequent spaced reviews, and practice GRE questions in context alongside vocabulary study.

## Revision

“Already gone through” lists only words from completed batches. Filter by due status or your latest revision rating, search by word, review due cards, or revise any word early.

**Review all words / resume** starts a saved pass through every learned word, ordered by earliest due timestamp (overdue first, future dates last). Each word appears once in that pass; ratings advance automatically. Returning to the overview or restarting does not lose the pass. Click the same button to resume. Newly graduated words join the next pass. Undo restores both the schedule and the queue position. Early reviews update FSRS just like individual reviews.

The study header shows the current card’s due date and time. After each rating, a confirmation shows that word’s freshly scheduled next review, even when the next card appears.

Revision uses the maintained `fsrs` Python package, at a 90% desired retention target. The three buttons map to Again, Good, and Easy. The scheduler stores each word's difficulty, stability, due time, and actual review history. Forgotten review words enter a 10-minute relearning step. They remain learned words rather than re-entering the new-word pool.

When a batch graduates, each word receives a conservative **Good initialization** at the graduation time. This seeds the first due date and is not counted as a revision attempt. Initial batch repetitions have their own history and do not inflate the FSRS revision count. Subsequent ratings—including early revision—update the schedule using the actual timestamp. Default FSRS weights are used; this version does not train personalized global weights from your history.

Dates are stored in UTC and displayed in your browser's local timezone. Overdue cards are offered first. The app recalculates the due count on visits; it does not require a background process while closed.

**Undo last rating** restores the previous streak, batch state, schedule, and history—even if the rating graduated a whole batch. Only the most recent rating can be undone. Starting a new batch ends the previous undo opportunity. A second browser tab can replace the displayed card; stale rating requests are rejected so they cannot count twice.

Shortcuts: Space reveals the full answer, 1/2/3 rate a recall, and U undoes the last rating. Standard keyboard activation also works on focused buttons. Rating controls appear only after a recall answer is revealed; teaching answers instead offer a neutral continuation action.

## Card content and layout

- One card per word, with all distinct source meanings preserved or represented in a merged meaning.
- Teaching front: word, pronunciation, type, verb forms where relevant, the primary retained meaning under **PLAIN MEANING**, and one corresponding complete example under **IN CONTEXT**. The target, known inflections, and relevant forms are highlighted. A missing primary example falls back to the first available example; empty optional content is not rendered.
- Recall/revision front: the same word metadata and a retrieval prompt, with an optional contextual hint containing one highlighted example but no definition. Hint visibility resets on every card and after reload/resume.
- Back: meanings, one concise example per displayed meaning, and up to three synonyms/antonyms. Some entries have no direct antonym. Where necessary, relation labels identify the grammatical use.
- Cards follow the reference's landscape 5:3 proportions. Long content can enlarge the card up to the available screen space and scroll; no meaning is clipped from the data and no card text is below 16 CSS pixels (12 points). The decorative hole is mirrored on the back.
- Dictionary cross-references and clear source errors received editorial corrections. Spelling and pronunciation generally follow the original material.
- Semantic preparation used `all-MiniLM-L6-v2` with a 0.78 cosine-similarity candidate threshold, followed by explicit editorial decisions. Cosine similarity is not a literal percentage of meaning. Additional paraphrases missed by the model were merged in the editorial pass. Distinctions such as **qualified** (trained / limited), **sanction** (approval / penalty), and **abridge** (shorten / restrict rights) are retained.
- The original source contains some general dictionary senses, abbreviations, and historical usages beyond typical GRE vocabulary. They remain available as requested. This is an edited study resource, not an assertion that every imported sense is equally useful for the GRE.

This flow teaches vocabulary explicitly before retrieval and keeps context available as scaffolding. It does not add fill-in-the-blank, multiple-choice, Sentence Equivalence, or generated-distractor practice. Those are separate possible enhancements. The FSRS algorithm, 90% retention target, rating mappings, and all vocabulary content are unchanged.

Use “View original source text” on a card to inspect the imported data. All rendered text is escaped, including source material; attached/source instructions are treated as content, not executable instructions.

## Data preservation and backups

SQLite contains the original **772,213-byte HTML snapshot**, its SHA-256 hash, all **995 original rows and 6,965 fields**, and separate cleaned cards. Original rows retain cell text and row markup. Each cleaned meaning references its original definition numbers. Source data is never overwritten by study actions.

The original `Words_With_Examples.html` can be deleted after setup: the app has been tested by starting with only a copy of SQLite in a separate directory. Retain the SQLite file and keep backups.

Use **Back up progress** to download a consistent SQLite backup, including both content and progress. To restore: stop the app, preserve your current database as a backup, then replace `data/flashcards.sqlite3` with the downloaded file and restart. Avoid overwriting a database while the app is running.

To deliberately reset all study progress while preserving content, stop the app and run:

```sh
.venv/bin/python scripts/reset_progress.py --confirm
```

## Implementation and tests

`app.py` contains the routes and transaction-based learning/review logic; `schema.sql` defines source records, cards, batches, members, schedules, events, the current presentation, and one-step undo. Active batch members store whether the current word has received its teaching exposure; existing in-progress databases add this flag without replacing cards, events, schedules, or progress. Presentation tokens and reveal checks prevent duplicate or stale teaching/rating actions. A unique index permits only one active batch. All mutations require an application-specific header. Requests must come directly from loopback with a local hostname or through the loopback Tailscale Serve proxy with an authenticated identity and `.ts.net` hostname. Study history is stored on the server, not in browser localStorage.

The browser UI lives in `templates/index.html`, `static/style.css`, and `static/app.js`. It loads no external fonts, scripts, or services.

Data preparation scripts are for development only; they are not invoked at startup. `data/content-overrides.json` is the canonical set of editorial decisions. `data/prepared.json` contains the original extraction and similarity scores. Do not rerun the editorial scripts casually: they are records of successive preparation passes. `scripts/update_content.py` rebuilds display content from the canonical preparation and overrides without replacing originals or study history.

Install development tools in the venv with `pip install -r requirements-dev.txt`, then:

```sh
.venv/bin/python -m pytest tests -q
.venv/bin/python tests/browser_check.py
```

The browser check requires Google Chrome at the standard macOS application path. It launches a temporary local server and uses an isolated temporary database, never the delivered study database. Backend tests also use temporary databases. Reports and screenshots are in `reports/`.

Algorithm reference: https://github.com/open-spaced-repetition/py-fsrs
Semantic model: https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2
GRE context: https://www.ets.org/gre/test-takers/general-test/prepare/content/verbal-reasoning.html

## Repository data

`data/seed.sqlite3` contains all vocabulary and the complete original HTML archive, with no study history. On first launch it initializes the ignored local `data/flashcards.sqlite3`. Existing local databases are never replaced. Virtual environments, model caches, personal progress, and generated screenshots/logs are excluded from Git. Use the app’s backup button to transfer your personal progress.
