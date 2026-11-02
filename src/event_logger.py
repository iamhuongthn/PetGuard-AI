import csv
from pathlib import Path

def write_events(rows, path):
    p=Path(path);p.parent.mkdir(parents=True,exist_ok=True)
    keys=['source','frame','video_seconds','pet_class','confidence','event']
    with p.open('w',newline='',encoding='utf-8') as f:
        writer=csv.DictWriter(f,fieldnames=keys)
        writer.writeheader();writer.writerows(rows)
    return p
