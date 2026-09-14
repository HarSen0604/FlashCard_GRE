# Wordwell — local GRE flashcards

A single-user Flask application with 995 cards, offline study, saved learning batches, and FSRS revision scheduling. All runtime data is in `data/flashcards.sqlite3`. The original HTML is **not required to run the app**.

## Start

Double-click `run.command` in Finder, or run:

```sh
cd FlashCard_GRE
.venv/bin/python app.py
```

Open **http://127.0.0.1:5055** in your browser. Stop with Ctrl+C. If the port is occupied, use `.venv/bin/python app.py --port 5057` and open that port instead. You do not need to activate the virtual environment when using these commands. The app listens only on the local laptop; no account, credentials, API key, or internet connection is needed for study.

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
2. Read the word, type, pronunciation, and verb forms where applicable. Recall the retained meanings in your own words, then reveal the answer.
3. Rate actual recall:
   - **I do not remember:** reset the word's consecutive-success streak to zero and repeat sooner.
   - **Remembered, needs revision:** add one success; repeat later.
   - **Easy to remember:** add one success; mark ready if the streak is at least three.
4. A successful third response of “needs revision” does **not** graduate the word; it remains until an Easy response. A later failure resets the streak even when it had reached three.
5. Repeats are separated by at least one other rated card whenever possible. Forgotten words receive a shorter queue delay (1 turn vs 3 for remembered and 5 for Easy); unseen words retain their randomized positions. If only one unfinished word remains, the server requires a 30-second gap instead. Reloading cannot bypass the gap.
6. Ready words stop repeating, but the **entire batch** stays in initial learning until every word is ready. Then all words move into **Already gone through** in one transaction.
7. Closing the browser or restarting the app preserves your exact batch and progress. Finish it before starting another new batch. Revision remains available meanwhile.

Learning is not a guarantee of long-term mastery. Use the subsequent spaced reviews, and practice GRE questions in context alongside vocabulary study.

## Revision

“Already gone through” lists only words from completed batches. Filter by due status or your latest revision rating, search by word, review due cards, or revise any word early.

**Review all words / resume** starts a saved pass through every learned word, ordered by earliest due timestamp (overdue first, future dates last). Each word appears once in that pass; ratings advance automatically. Returning to the overview or restarting does not lose the pass. Click the same button to resume. Newly graduated words join the next pass. Undo restores both the schedule and the queue position. Early reviews update FSRS just like individual reviews.

The study header shows the current card’s due date and time. After each rating, a confirmation shows that word’s freshly scheduled next review, even when the next card appears.

Revision uses the maintained `fsrs` Python package, at a 90% desired retention target. The three buttons map to Again, Good, and Easy. The scheduler stores each word's difficulty, stability, due time, and actual review history. Forgotten review words enter a 10-minute relearning step. They remain learned words rather than re-entering the new-word pool.

When a batch graduates, each word receives a conservative **Good initialization** at the graduation time. This seeds the first due date and is not counted as a revision attempt. Initial batch repetitions have their own history and do not inflate the FSRS revision count. Subsequent ratings—including early revision—update the schedule using the actual timestamp. Default FSRS weights are used; this version does not train personalized global weights from your history.

Dates are stored in UTC and displayed in your browser's local timezone. Overdue cards are offered first. The app recalculates the due count on visits; it does not require a background process while closed.

**Undo last rating** restores the previous streak, batch state, schedule, and history—even if the rating graduated a whole batch. Only the most recent rating can be undone. Starting a new batch ends the previous undo opportunity. A second browser tab can replace the displayed card; stale rating requests are rejected so they cannot count twice.

Shortcuts: Space to reveal, 1/2/3 to rate, U to undo. Standard keyboard activation also works on focused buttons. Rating controls appear only after revealing the answer.

## Card content and layout

- One card per word, with all distinct source meanings preserved or represented in a merged meaning.
- Front: word, pronunciation, type, and present/past/future/past participle for verbs. Inflected headwords such as **bent** use their base verb (**bend**) for the forms. Words with multiple grammatical uses list the relevant types.
- Back: meanings, one concise example per displayed meaning, and up to three synonyms/antonyms. Some entries have no direct antonym. Where necessary, relation labels identify the grammatical use.
- Cards follow the reference's landscape 5:3 proportions. Long content can enlarge the card up to the available screen space and scroll; no meaning is clipped from the data and no card text is below 16 CSS pixels (12 points). The decorative hole is mirrored on the back.
- Dictionary cross-references and clear source errors received editorial corrections. Spelling and pronunciation generally follow the original material.
- Semantic preparation used `all-MiniLM-L6-v2` with a 0.78 cosine-similarity candidate threshold, followed by explicit editorial decisions. Cosine similarity is not a literal percentage of meaning. Additional paraphrases missed by the model were merged in the editorial pass. Distinctions such as **qualified** (trained / limited), **sanction** (approval / penalty), and **abridge** (shorten / restrict rights) are retained.
- The original source contains some general dictionary senses, abbreviations, and historical usages beyond typical GRE vocabulary. They remain available as requested. This is an edited study resource, not an assertion that every imported sense is equally useful for the GRE.

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

`app.py` contains the routes and transaction-based learning/review logic; `schema.sql` defines source records, cards, batches, members, schedules, events, the current presentation, and one-step undo. Presentation tokens and reveal checks prevent duplicate or stale ratings. A unique index permits only one active batch. All mutations require an application-specific header and the local hostname. Study history is stored on the server, not in browser localStorage.

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
