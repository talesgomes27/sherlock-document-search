"""Evaluate the approved v2 final split with frozen methods and no new selection."""

import argparse
from collections import Counter
import hashlib
import json
from numbers import Real
from pathlib import Path
import re

from .bm25 import BM25Search
from .corpus import prepare_corpus
from .development import verify_freeze
from .final_evaluation import runtime_versions, verify_sources
from .search import literal_search
from .tfidf import TfidfSearch
from .v2_development import metrics, valid_negative_evidence, validate_output, verify_preservation


FINAL_PATH = 'data/processed/v2_holdout/final.json'
BM25_CONFIG = {'k1': 1.2, 'b': 0.75, 'min_score': 0.0}
FINAL_TYPES = {'exact': 6, 'paraphrase': 6, 'context': 6, 'unanswerable': 6}
REQUIRED_FROZEN_PATHS = (
    'src/sherlock_search/v2_final.py', 'src/sherlock_search/bm25.py',
    'src/sherlock_search/v2_development.py', 'src/sherlock_search/development.py',
    'src/sherlock_search/final_evaluation.py', 'src/sherlock_search/corpus.py',
    'src/sherlock_search/search.py', 'src/sherlock_search/tfidf.py',
    'src/sherlock_search/tfidf_config.json', 'src/sherlock_search/corpus_manifest.json',
    'evaluation/v2/protocol.json', 'evaluation/v2/development.json',
    'evaluation/v2/configuration_decision.json', 'evaluation/v2/holdout_manifest.json',
    'evaluation/v2/v1_preservation.json', 'evaluation/m3_freeze.json',
    'reports/v2/development.approved.json', FINAL_PATH,
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_freeze_v2(root: Path) -> dict:
    """Validate frozen inputs, imported sources and runtime before opening queries."""
    root = Path(root).resolve()
    snapshot = json.loads((root / 'evaluation/v2/freeze.json').read_text(encoding='utf-8'))
    if (not isinstance(snapshot, dict) or not isinstance(snapshot.get('scope'), str)
            or not snapshot['scope'].strip() or snapshot.get('final_queries_executed') is not False
            or not isinstance(snapshot.get('file_sha256'), dict)
            or not set(REQUIRED_FROZEN_PATHS).issubset(snapshot['file_sha256'])):
        raise ValueError('Manifesto congelado v2 inválido ou incompleto.')
    configuration = snapshot.get('bm25')
    if (not isinstance(configuration, dict) or configuration != BM25_CONFIG
            or any(isinstance(value, bool) or not isinstance(value, Real) for value in configuration.values())):
        raise ValueError('BM25 final deve manter k1=1.2, b=0.75 e min_score=0, sem nova seleção.')
    for relative, expected in snapshot['file_sha256'].items():
        if (not isinstance(relative, str) or not relative or Path(relative).is_absolute()
                or '\\' in relative or Path(relative).as_posix() != relative
                or '..' in Path(relative).parts
                or not isinstance(expected, str) or re.fullmatch(r'[0-9a-f]{64}', expected) is None):
            raise ValueError('Manifesto congelado v2 contém caminho ou SHA-256 inválido.')
        path = (root / relative).resolve()
        if not path.is_relative_to(root):
            raise ValueError('Manifesto congelado v2 contém caminho fora do projeto.')
        if sha256(path) != expected:
            raise ValueError(f'Arquivo congelado v2 divergente: {relative}')
    versions = runtime_versions()
    if versions['python'] != '3.11.17' or versions != snapshot.get('runtime_versions'):
        raise ValueError('Runtime divergente do congelamento v2; Python exato 3.11.17 é obrigatório.')
    verify_sources(root, snapshot)
    protocol = json.loads((root / 'evaluation/v2/protocol.json').read_text(encoding='utf-8'))
    final = protocol.get('final') if isinstance(protocol, dict) else None
    counts = {'queries': 24, 'answerable': 18, 'unanswerable': 6}
    if (not isinstance(final, dict)
            or any(type(final.get(key)) is not int or final[key] != value for key, value in counts.items())
            or final.get('query_types') != FINAL_TYPES
            or any(type(value) is not int for value in final['query_types'].values())
            or protocol.get('bm25') != {'k1': 1.2, 'b': 0.75}
            or protocol.get('thresholds') != [0, 0.5, 1, 2, 4, 8, 16, 32]
            or any(isinstance(value, bool) for value in protocol['thresholds'])
            or protocol.get('selection_rule') != 'maximize_balanced_utility_then_minimize_false_positive_rate_then_minimize_threshold'
            or protocol.get('final_queries_executed') is not False):
        raise ValueError('Protocolo final v2 divergente dos parâmetros pré-definidos.')
    decision = json.loads((root / 'evaluation/v2/configuration_decision.json').read_text(encoding='utf-8'))
    if (not isinstance(decision, dict) or decision.get('bm25') != configuration
            or any(isinstance(value, bool) for value in decision['bm25'].values())):
        raise ValueError('Decisão de configuração divergente do BM25 congelado.')
    return snapshot


def load_final(root: Path) -> list[dict]:
    """Read only the fixed approved v2 holdout path; no query-file option exists."""
    root = Path(root).resolve()
    path = root / FINAL_PATH
    if path.is_symlink() or not path.resolve().is_relative_to(root):
        raise ValueError('Teste final v2 deve ser um arquivo próprio dentro do projeto.')
    data = path.read_bytes()
    queries = json.loads(data)
    manifest = json.loads((root / 'evaluation/v2/holdout_manifest.json').read_text(encoding='utf-8'))
    counts = {'query_count': 24, 'positive': 18, 'negative': 6}
    if (not isinstance(manifest, dict) or manifest.get('split') != 'v2_final'
            or manifest.get('status') != 'approved_not_evaluated'
            or manifest.get('final_queries_executed') is not False
            or manifest.get('json_path') != FINAL_PATH
            or manifest.get('json_sha256') != hashlib.sha256(data).hexdigest()
            or any(type(manifest.get(key)) is not int or manifest[key] != value for key, value in counts.items())
            or manifest.get('type_counts') != FINAL_TYPES
            or any(type(value) is not int for value in manifest['type_counts'].values())):
        raise ValueError('Metadados ou aprovação do teste final v2 inválidos.')
    if (not isinstance(queries, list) or len(queries) != 24
            or any(not isinstance(query, dict) for query in queries)
            or [query.get('id') for query in queries] != [f'v2-final-{number:02}' for number in range(1, 25)]):
        raise ValueError('São necessárias as 24 consultas finais v2 com IDs fixos.')
    for query in queries:
        references = query.get('relevant_ids')
        if (type(query.get('answerable')) is not bool or query.get('review_status') != 'approved'
                or not isinstance(query.get('query'), str) or not query['query'].strip()
                or not isinstance(query.get('rationale'), str) or not query['rationale'].strip()
                or not isinstance(references, list)
                or any(not isinstance(reference, str) or not reference.strip() for reference in references)
                or len(set(references)) != len(references)
                or bool(references) != query['answerable']
                or not isinstance(query.get('query_type'), str) or query['query_type'] not in FINAL_TYPES
                or (query['query_type'] == 'unanswerable') != (not query['answerable'])
                or (not query['answerable'] and not valid_negative_evidence(query.get('negative_verification')))):
            raise ValueError(f'Consulta ou rótulo final v2 inválido: {query.get("id")}')
    if (sum(query['answerable'] for query in queries) != 18
            or Counter(query['query_type'] for query in queries) != FINAL_TYPES):
        raise ValueError('Composição final v2 deve conter 18 positivas e 6 negativas, com 6 de cada tipo.')
    return queries


def evaluate_final(root: Path, raw_dir: Path) -> dict:
    root, raw_dir = Path(root).resolve(), Path(raw_dir).resolve()
    frozen = verify_freeze_v2(root)
    freeze_hash = sha256(root / 'evaluation/v2/freeze.json')
    preserved = verify_preservation(root)
    v1 = verify_freeze(root)
    if len(preserved['file_sha256']) != 35 or len(v1['file_sha256']) != 15:
        raise ValueError('Preservação exige os 35 ativos v1 e os 15 arquivos M3 congelados.')
    versions = runtime_versions()
    if versions != v1['runtime_versions']:
        raise ValueError('Runtime divergente da v1 congelada.')
    verify_sources(root, v1)
    queries = load_final(root)
    paragraphs, corpus = prepare_corpus(raw_dir)
    source_ids = {paragraph['id'] for paragraph in paragraphs}
    for query in queries:
        references = query['relevant_ids'] if query['answerable'] else query['negative_verification']['evidence_ids']
        if any(reference not in source_ids for reference in references):
            raise ValueError('Referência positiva ou de verificação negativa ausente no corpus final v2.')
    tfidf = TfidfSearch(paragraphs)
    if tfidf.min_score != v1['tfidf']['min_score']:
        raise ValueError('min_score TF-IDF divergente da v1 congelada.')
    bm25 = BM25Search(paragraphs, **frozen['bm25'])
    predictions = {
        'literal_v1': {query['id']: literal_search(paragraphs, query['query']) for query in queries},
        'tfidf_v1': {query['id']: tfidf.search(query['query']) for query in queries},
        'bm25': {query['id']: bm25.search(query['query']) for query in queries},
    }
    if (verify_freeze_v2(root) != frozen
            or sha256(root / 'evaluation/v2/freeze.json') != freeze_hash
            or verify_preservation(root) != preserved or verify_freeze(root) != v1):
        raise ValueError('Manifesto ou insumos congelados alterados durante a avaliação final v2.')
    verify_sources(root, v1)
    if {path.name for path in raw_dir.glob('*.txt') if path.is_file()} != {source['filename'] for source in corpus['files']}:
        raise ValueError('Inventário do corpus alterado durante a avaliação final v2.')
    for source in corpus['files']:
        if sha256(raw_dir / source['filename']) != source['sha256']:
            raise ValueError(f'Corpus alterado durante a avaliação final v2: {source["filename"]}')
    return {
        'split': 'v2_final', 'annotation_status': 'approved', 'query_count': len(queries),
        'counts': {'answerable': 18, 'unanswerable': 6, 'query_types': FINAL_TYPES},
        'methods': {name: metrics(queries, values) for name, values in predictions.items()},
        'results': [{'id': query['id'], 'answerable': query['answerable'],
                     'known_relevant_ids': query['relevant_ids'],
                     **{name: [{'id': row['id'], 'score': row['score']} for row in values[query['id']]]
                        for name, values in predictions.items()}} for query in queries],
        'configuration': {'bm25': frozen['bm25'], 'tfidf_v1': v1['tfidf'], 'top_k': 5},
        'versions': versions, 'input_sha256': dict(sorted(frozen['file_sha256'].items())),
        'freeze_sha256': freeze_hash, 'corpus_totals': corpus['totals'],
        'v1_preserved': True, 'final_v2_executed': True,
    }


def validate_final_output(root: Path, output: Path, frozen: dict) -> Path:
    if output.is_symlink():
        raise ValueError('A saída final deve ser um arquivo próprio, sem redirecionamento.')
    output = validate_output(root, output)
    protected = [root / relative for relative in frozen['file_sha256']]
    protected.append(root / 'evaluation/v2/freeze.json')
    if any(output == path.resolve() or (output.exists() and path.exists() and output.samefile(path))
           for path in protected):
        raise ValueError('A saída final não pode sobrescrever nenhum insumo congelado.')
    return output


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path('.'))
    parser.add_argument('--raw-dir', type=Path, default=Path('data/raw'))
    parser.add_argument('--output', type=Path, default=Path('reports/v2/final.json'))
    args = parser.parse_args()
    root = args.root.resolve()
    try:
        frozen = verify_freeze_v2(root)
        output = validate_final_output(root, root / args.output, frozen)
        report = evaluate_final(root, (root / args.raw_dir).resolve())
        validate_final_output(root, output, frozen)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    except (OSError, ValueError, KeyError, TypeError) as error:
        parser.error(str(error))
    print(f'Teste final v2: {report["query_count"]} consultas aprovadas; relatório: {output}')
    for name, row in report['methods'].items():
        print(f'{name}: hits conhecidos {row["positive_hits"]}/{row["positive_queries"]}; '
              f'negativas com retorno {row["false_positive_queries"]}/{row["negative_queries"]}')


if __name__ == '__main__':
    main()
