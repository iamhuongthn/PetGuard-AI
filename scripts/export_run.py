"""Copy a Colab run's video, CSV, config and screenshots to a ZIP for safekeeping."""
import argparse, shutil, zipfile
from pathlib import Path

def export(run, destination):
    run=Path(run).resolve(); destination=Path(destination).resolve()
    if not run.is_dir(): raise FileNotFoundError(run)
    required=['zone_config.json','events.csv','frame_predictions.csv']
    missing=[x for x in required if not (run/x).is_file()]
    if missing: raise FileNotFoundError('Missing run outputs: '+', '.join(missing))
    destination.parent.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(destination,'w',zipfile.ZIP_DEFLATED) as z:
        for f in run.rglob('*'):
            if f.is_file(): z.write(f, f.relative_to(run.parent))
    return destination

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('run_folder');parser.add_argument('--output',default='petguard_run_export.zip');args=parser.parse_args()
    print(export(args.run_folder,args.output))
