#!/usr/bin/env python3
import csv
import time
import requests
from urllib.parse import urljoin

INPUT='data/schools.csv'
OUTPUT='data/study_tours.csv'
KEYWORDS=['study tour','study tours','school tour','school tours','international students','visits','visitor','education tour']
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

with open(INPUT,newline='',encoding='utf-8') as f_in, open(OUTPUT,'w',newline='',encoding='utf-8') as f_out:
    reader=csv.DictReader(f_in)
    fieldnames=list(reader.fieldnames)+['offers_study_tour','matched_keyword','checked_url','http_status','error']
    writer=csv.DictWriter(f_out,fieldnames=fieldnames)
    writer.writeheader()

    for row in reader:
        # only consider primary schools
        sch_type=row.get('sch_desc','') or row.get('sch_type','') or ''
        if 'primary' not in sch_type.lower():
            continue
        homepage=row.get('sch_homepage','') or ''
        if not homepage:
            row.update({'offers_study_tour':'unknown','matched_keyword':'','checked_url':'','http_status':'','error':'no homepage'})
            writer.writerow(row)
            continue
        url=normalize(homepage)
        matched=''
        status=''
        err=''
        try:
            r=requests.get(url, headers=HEADERS, timeout=TIMEOUT, allow_redirects=True)
            status=str(r.status_code)
            text=(r.text or '').lower()
            for k in KEYWORDS:
                if k in text:
                    matched=k
                    break
            # also try common subpages if not found
            if not matched:
                for sub in ['/about','/about-us','/international','/visitors','/our-school']:
                    try:
                        r2=requests.get(urljoin(url,sub), headers=HEADERS, timeout=TIMEOUT)
                        if r2.status_code==200 and any(k in (r2.text or '').lower() for k in KEYWORDS):
                            matched=';'.join([k for k in KEYWORDS if k in (r2.text or '').lower()])
                            status=str(r2.status_code)
                            url=urljoin(url,sub)
                            break
                    except Exception:
                        pass
        except Exception as e:
            err=str(e)
        offers='yes' if matched else 'no'
        row.update({'offers_study_tour':offers,'matched_keyword':matched,'checked_url':url,'http_status':status,'error':err})
        writer.writerow(row)
        time.sleep(RATE)

print('Done. Results saved to', OUTPUT)
