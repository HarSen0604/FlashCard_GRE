"""Explicit local reset. Preserves all original data and cleaned flashcards."""
import argparse,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from app import connect
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--confirm',action='store_true');args=p.parse_args()
if not args.confirm:p.error('Stop the app, back up your database, then pass --confirm to erase study progress.')
with connect(ROOT/'data/flashcards.sqlite3') as db:
    db.execute('BEGIN IMMEDIATE')
    for table in ['actions','presentation','events','schedules','members','batches']:db.execute('DELETE FROM '+table)
    assert db.execute('SELECT count(*) FROM cards').fetchone()[0]==995
    assert db.execute('SELECT count(*) FROM originals').fetchone()[0]==995
print('Clean slate: 995 cards, zero batches, zero ratings, zero revision history. Original data preserved.')
