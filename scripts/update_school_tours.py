#!/usr/bin/env python3
import time
import argparse
import requests
from urllib.parse import urljoin
from app import create_app, db
from app.models import School
from sqlalchemy import text

KEYWORDS=['study tour','study tours','school tour','school tours','education tour']
HEADERS={'User-Agent':'Mozilla/5.0 (compatible; study-tour-bot/1.0; +https://github.com)'}
RATE=1.0
TIMEOUT=10


def normalize(u):
    if not u:
        return ''
    u=u.strip()
    if u and not u.startswith('http'):
        u='http://'+u
    return u


def check_homepage(url):
    try:
        r=requests.get(url, headers=HEADERS, timeout=TIMEOUT, allow_redirects=True)
        if r.status_code!=200:
            return False, '', str(r.status_code)
        text=(r.text or '').lower()
        for k in KEYWORDS:
            if k in text:
                return True, k, str(r.status_code)
        # try common subpages
        for sub in ['/about','/about-us','/international','/visitors','/our-school']:
            try:
                r2=requests.get(urljoin(url,sub), headers=HEADERS, timeout=TIMEOUT)
                if r2.status_code==200:
                    t=(r2.text or '').lower()
                    for k in KEYWORDS:
                        if k in t:
                            return True, k, str(r2.status_code)
            except Exception:
                continue
        return False, '', str(r.status_code)
    except Exception as e:
        return False, '', str(e)


if __name__=='__main__':
    parser = argparse.ArgumentParser(description='Crawl school homepages and update tour flag')
    parser.add_argument('--limit', type=int, default=0, help='Limit number of primary schools to check (0 = all)')
    parser.add_argument('--rate', type=float, default=None, help='Seconds to sleep between requests (overrides script RATE)')
    parser.add_argument('--dry-run', action='store_true', help='Do not write changes to the database')
    args = parser.parse_args()

    if args.rate is not None:
        RATE = float(args.rate)

    app = create_app()
    with app.app_context():
        # ensure table has new column
        db.create_all()
        # Ensure 'tour' column exists (SQLite won't add columns via create_all on existing tables)
        try:
            res = db.session.execute(text("PRAGMA table_info('school')")).fetchall()
            cols = [r[1] for r in res]
            if 'tour' not in cols:
                print("Adding 'tour' column to school table...")
                db.session.execute(text("ALTER TABLE school ADD COLUMN tour BOOLEAN NOT NULL DEFAULT 0"))
                db.session.commit()
        except Exception as e:
            print('Could not ensure tour column exists:', e)

        # Query primary schools (use either sch_desc or sch_type)
        schools = School.query.all()
        total = len(schools)
        print(f'Checking up to {args.limit or "all"} primary schools (found {total} total schools)...')
        processed = 0
        idx = 0
        for s in schools:
            idx += 1
            stype = (s.sch_desc or '') + ' ' + (s.sch_type or '')

            if args.limit and processed >= args.limit:
                print('Limit reached; stopping.')
                break

            processed += 1
            homepage = s.sch_homepage or ''
            if not homepage:
                s.tour = False
                if not args.dry_run:
                    db.session.add(s)
                    db.session.commit()
                print(f'[{idx}/{total}] {s.sch_name}: no homepage (tour=False)')
                continue

            url = normalize(homepage)
            print(f'[{idx}/{total}] [{processed}] Checking {s.sch_name} -> {url}')
            offers, matched, status = check_homepage(url)
            s.tour = bool(offers)
            if not args.dry_run:
                db.session.add(s)
                db.session.commit()
            print(f'    matched={matched or "-"} status={status or "-"} tour={s.tour}')
            time.sleep(RATE)

        print('Done.')
