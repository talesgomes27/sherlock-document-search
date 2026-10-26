"""Read public frozen results for the report without importing retrieval or reading books."""

import hashlib
import json
from pathlib import Path
import re


def verify_report_sources(root):
    root=Path(root).resolve()
    def read(name):
        if (not isinstance(name,str) or not name or Path(name).is_absolute()
                or '..' in Path(name).parts or '\\' in name or Path(name).as_posix()!=name):
            raise ValueError(f'Caminho inválido no manifesto: {name}')
        path=(root/name).resolve()
        if not path.is_relative_to(root):
            raise ValueError(f'Caminho fora do projeto: {name}')
        return path.read_bytes()
    def sha(content):
        return hashlib.sha256(content).hexdigest()
    report_bytes=read('reports/v2/final.json')
    validation=json.loads(read('reports/v2/validation.json'))
    if sha(report_bytes)!=validation['final_report_sha256']:
        raise ValueError('Relatório final v2 divergente da validação.')
    v2=json.loads(report_bytes)
    freeze_bytes=read('evaluation/v2/freeze.json')
    if sha(freeze_bytes)!=v2['freeze_sha256']:
        raise ValueError('Manifesto congelado v2 divergente do relatório final.')
    frozen=json.loads(freeze_bytes)['file_sha256']
    if not isinstance(frozen,dict) or not frozen:
        raise ValueError('Manifesto congelado vazio ou inválido.')
    hashes={}
    for name,expected in frozen.items():
        source='evaluation/v2/final.json' if name=='data/processed/v2_holdout/final.json' else name
        actual=sha(read(source))
        if not isinstance(expected,str) or not re.fullmatch('[0-9a-f]{64}',expected) or actual!=expected:
            raise ValueError(f'Arquivo congelado divergente: {name}')
        hashes[name]=actual
    hashes['reports/v2/final.json']=sha(report_bytes)
    hashes['evaluation/v2/freeze.json']=sha(freeze_bytes)
    return {'v1':json.loads(read('reports/m4_final.json')), 'v2':v2,
            'corpus':json.loads(read('reports/m1_quality.json')),
            'queries_v2':json.loads(read('evaluation/v2/final.json')),
            'decision':json.loads(read('evaluation/v2/configuration_decision.json')),
            'source_hashes':hashes}


if __name__=='__main__':
    result=verify_report_sources(Path(__file__).resolve().parents[1])
    print(f"Fontes do relatório conferidas: {len(result['source_hashes'])} hashes; nenhum modelo executado.")
