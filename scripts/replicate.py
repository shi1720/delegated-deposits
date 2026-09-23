"""Offline numerical replication using archived FDIC responses."""
from pathlib import Path
import os,subprocess,sys
ROOT=Path(__file__).resolve().parents[1]
env=os.environ.copy();env['PYTHONPATH']=str(ROOT/'src')
for command in [[sys.executable,'-m','pytest','-q','-W','error']]+[
        [sys.executable,'scripts/'+name] for name in [
            'run_experiments.py','refine_bounds.py','analyze_banks.py',
            'make_figures.py','make_tables.py','verify_results.py']]:
    subprocess.run(command,cwd=ROOT,env=env,check=True)
print('Offline replication completed. Compile the PDF separately with scripts/build_paper.py.')
