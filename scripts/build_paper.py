"""Compile the manuscript and reject unresolved citations or overfull boxes."""
from pathlib import Path
import argparse,shutil,subprocess,sys
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--tectonic',default='tectonic');args=p.parse_args()
engine=shutil.which(args.tectonic)
if engine is None:raise SystemExit('Install Tectonic or pass --tectonic /path/to/tectonic.')
tmp=ROOT/'tmp/pdfs';tmp.mkdir(parents=True,exist_ok=True)
run=subprocess.run([engine,'--keep-logs','--keep-intermediates','--outdir',str(tmp),'main.tex'],
                   cwd=ROOT/'paper',text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
(tmp/'compiler-output.txt').write_text(run.stdout)
if run.returncode:print(run.stdout[-6000:]);raise SystemExit(run.returncode)
log=(tmp/'main.log').read_text()
bad=[line for line in log.splitlines() if any(s in line for s in ['Overfull','undefined','LaTeX Error'])]
if bad:print('\n'.join(bad));raise SystemExit('Resolve typesetting issues before delivery.')
dest=ROOT/'output/pdf/Gupta_Delegated_Deposit_Control.pdf'
dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(tmp/'main.pdf',dest)
print(dest)
