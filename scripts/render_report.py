"""Render the Quarto report from frozen public results in a separate Jupyter environment."""

import hashlib
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import tempfile
from datetime import datetime, timezone

from verify_report_sources import verify_report_sources


ROOT=Path(__file__).resolve().parents[1]


def main():
    data=verify_report_sources(ROOT)
    version=subprocess.check_output(['quarto','--version'],text=True).strip()
    if version!='1.10.19':
        raise ValueError('Use Quarto 1.10.19 para reproduzir esta publicação.')
    with tempfile.TemporaryDirectory(prefix='sherlock-report-') as directory:
        env=os.environ.copy()
        env['QUARTO_PYTHON']=sys.executable
        env['JUPYTER_PATH']=str(Path(sys.prefix)/'share/jupyter')
        env['IPYTHONDIR']=str(Path(directory)/'ipython')
        env['JUPYTER_RUNTIME_DIR']=str(Path(directory)/'runtime')
        subprocess.run([sys.executable,'-m','ipykernel','install','--prefix',sys.prefix,
                        '--name','sherlock-report','--display-name','Sherlock report'],
                       check=True,env=env,capture_output=True,text=True)
        subprocess.run(['quarto','render','site','--to','html'],cwd=ROOT,env=env,check=True)
    if verify_report_sources(ROOT)['source_hashes']!=data['source_hashes']:
        raise ValueError('Fontes alteradas durante a renderização.')
    output=ROOT/'site/_site'
    commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    metadata={'source_commit':commit,
              'source_tree_dirty':bool(subprocess.check_output(['git','status','--porcelain'],cwd=ROOT,text=True).strip()),
              'workflow_run_id':os.environ.get('GITHUB_RUN_ID'),'built_at_utc':datetime.now(timezone.utc).isoformat(),
              'quarto_version':version,'python_version':platform.python_version(),
              'final_report_sha256':data['source_hashes']['reports/v2/final.json'],
              'input_sha256':data['source_hashes'],
              'output_sha256':{p.relative_to(output).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()
                               for p in sorted(output.rglob('*')) if p.is_file() and p.name!='_build.json'}}
    (output/'_build.json').write_text(json.dumps(metadata,indent=2)+'\n',encoding='utf-8')
    print(f'Relatório renderizado: {len(metadata["output_sha256"])} arquivos; fontes verificadas.')


if __name__=='__main__':main()
