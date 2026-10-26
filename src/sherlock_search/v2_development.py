"""Compare v1 baselines and BM25 using only the new development proposals."""

import argparse
from collections import Counter
from fractions import Fraction
import math
from numbers import Real
import hashlib
import json
from pathlib import Path
from time import perf_counter

from .bm25 import BM25Search
from .corpus import prepare_corpus
from .development import summarize, verify_freeze
from .final_evaluation import runtime_versions, verify_sources
from .search import literal_search
from .tfidf import TfidfSearch


def verify_preservation(root: Path) -> dict:
    manifest = json.loads((root / 'evaluation/v2/v1_preservation.json').read_text(encoding='utf-8'))
    for name, expected in manifest['file_sha256'].items():
        path = (root / name).resolve()
        if not path.is_relative_to(root.resolve()) or hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            raise ValueError(f'Arquivo v1 alterado: {name}')
    return manifest


def load_development(root: Path, *, allow_proposed: bool = False) -> list[dict]:
    path = root / 'evaluation/v2/development.json'
    if path.is_symlink():
        raise ValueError('Desenvolvimento deve ser um arquivo próprio, sem redirecionamento.')
    queries = json.loads(path.read_text(encoding='utf-8'))
    protocol = json.loads((root / 'evaluation/v2/protocol.json').read_text(encoding='utf-8'))['development']
    expected = {'queries': 36, 'answerable': 27, 'unanswerable': 9}
    if (any(type(protocol.get(key)) is not int or protocol[key] != value for key, value in expected.items())
            or protocol.get('query_types') != {'exact': 9, 'paraphrase': 9, 'context': 9, 'unanswerable': 9}
            or any(type(value) is not int for value in protocol['query_types'].values())):
        raise ValueError('Composição de desenvolvimento inválida no protocolo.')
    if not isinstance(queries, list) or len(queries) != protocol['queries']:
        raise ValueError('Contagem de desenvolvimento divergente do protocolo.')
    if any(not isinstance(q, dict) for q in queries) or [q.get('id') for q in queries] != [f'v2-dev-{i:02}' for i in range(1, 37)]:
        raise ValueError('IDs de desenvolvimento inválidos; teste reservado não é uma entrada permitida.')
    for query in queries:
        refs = query.get('relevant_ids')
        if (type(query.get('answerable')) is not bool or not isinstance(query.get('query'), str)
                or not query['query'].strip() or not isinstance(refs, list)
                or any(not isinstance(ref, str) or not ref for ref in refs)
                or len(set(refs)) != len(refs) or bool(refs) != query['answerable']
                or query.get('review_status') not in ('proposed', 'approved')
                or query.get('query_type') not in protocol['query_types']
                or (query['query_type'] == 'unanswerable') != (not query['answerable'])
                or not isinstance(query.get('rationale'), str) or not query['rationale'].strip()
                or (not query['answerable'] and not valid_negative_evidence(query.get('negative_verification')))):
            raise ValueError(f'Consulta ou rótulo inválido: {query.get("id")}')
    if (sum(q['answerable'] for q in queries) != protocol['answerable']
            or sum(not q['answerable'] for q in queries) != protocol['unanswerable']
            or Counter(q['query_type'] for q in queries) != protocol['query_types']):
        raise ValueError('Composição de desenvolvimento divergente do protocolo.')
    if not allow_proposed and any(q['review_status'] != 'approved' for q in queries):
        raise ValueError('Rótulos proposed exigem revisão; use --allow-proposed somente para exploração.')
    return queries


def valid_negative_evidence(evidence) -> bool:
    if not isinstance(evidence, dict):
        return False
    for key in ('method', 'kind', 'finding', 'scope', 'uncertainty'):
        if not isinstance(evidence.get(key), str) or not evidence[key].strip():
            return False
    refs = evidence.get('evidence_ids')
    return (isinstance(refs, list) and bool(refs)
            and all(isinstance(ref, str) and ref.strip() for ref in refs)
            and len(set(refs)) == len(refs))


def metrics(queries: list[dict], predictions: dict) -> dict:
    result = summarize(queries, predictions)
    reciprocal_ranks = []
    for query in queries:
        if query['answerable']:
            known = set(query['relevant_ids'])
            reciprocal_ranks.append(next((1 / rank for rank, row in enumerate(predictions[query['id']][:5], 1)
                                          if row['id'] in known), 0))
    result['mrr_at_5'] = sum(reciprocal_ranks) / len(reciprocal_ranks)
    result['positive_queries_without_results'] = sum(q['answerable'] and not predictions[q['id']] for q in queries)
    return result


def choose_threshold(candidates: list[dict]) -> float:
    def order(row):
        negative_rate = Fraction(row['false_positive_queries'], row['negative_queries'])
        utility = (Fraction(row['positive_hits'], row['positive_queries']) + 1 - negative_rate) / 2
        return -utility, negative_rate, row['min_score']
    return min(candidates, key=order)['min_score']


def compare_development(paragraphs: list[dict], queries: list[dict], protocol: dict) -> dict:
    thresholds = protocol['thresholds']
    if (not isinstance(thresholds, list) or not thresholds
            or any(isinstance(value, bool) or not isinstance(value, Real) or not math.isfinite(value) or value < 0 for value in thresholds)
            or thresholds[0] != 0 or thresholds != sorted(set(thresholds))
            or protocol['selection_rule'] != 'maximize_balanced_utility_then_minimize_false_positive_rate_then_minimize_threshold'):
        raise ValueError('Grade ou regra de seleção inválida.')
    source_ids = {p['id'] for p in paragraphs}
    if any(ref not in source_ids for q in queries for ref in q['relevant_ids']):
        raise ValueError('Referência de desenvolvimento ausente no corpus.')
    for query in queries:
        evidence = query.get('negative_verification', {})
        if not query['answerable'] and any(ref not in source_ids for ref in evidence.get('evidence_ids', [])):
            raise ValueError('Referência de verificação negativa ausente no corpus.')
    predictions, timings = {}, {}
    for name, factory in [('literal_v1', None), ('tfidf_v1', lambda: TfidfSearch(paragraphs)),
                          ('bm25_uncut', lambda: BM25Search(paragraphs, **protocol['bm25']))]:
        start = perf_counter()
        index = factory() if factory else None
        built = perf_counter()
        predictions[name] = {q['id']: index.search(q['query']) if index else literal_search(paragraphs, q['query']) for q in queries}
        elapsed = perf_counter() - built
        timings[name] = {'index_seconds': built - start, 'queries_seconds': elapsed,
                         'mean_query_ms': elapsed * 1000 / len(queries)}
    raw = predictions['bm25_uncut']
    candidates = []
    for threshold in protocol['thresholds']:
        filtered = {key: [row for row in rows if row['score'] >= threshold] for key, rows in raw.items()}
        candidates.append({'min_score': threshold, **metrics(queries, filtered)})
    selected = choose_threshold(candidates)
    predictions['bm25_candidate'] = {key: [row for row in rows if row['score'] >= selected] for key, rows in raw.items()}
    proposed = any(q['review_status'] != 'approved' for q in queries)
    return {
        'split': 'v2_development', 'query_count': len(queries),
        'purpose': 'development_not_independent_test', 'annotation_status': 'proposed' if proposed else 'approved',
        'candidate_provisional': proposed, 'candidate_applied_to_runtime': False,
        'bm25': protocol['bm25'], 'selection_rule': protocol['selection_rule'],
        'threshold_grid': candidates, 'candidate_min_score': selected,
        **{name: metrics(queries, values) for name, values in predictions.items()},
        'timings': timings,
        'results': [{'id': q['id'], 'answerable': q['answerable'], 'known_relevant_ids': q['relevant_ids'],
                     **{name: [{'id': row['id'], 'score': row['score']} for row in values[q['id']]]
                        for name, values in predictions.items()}} for q in queries],
    }


def run_development(root: Path, raw_dir: Path, *, allow_proposed: bool = False) -> dict:
    before = verify_preservation(root)
    frozen = verify_freeze(root)
    verify_sources(root, frozen)
    versions = runtime_versions()
    if versions != frozen['runtime_versions']:
        raise ValueError('Runtime divergente da v1; mantenha o ambiente congelado para esta comparação.')
    queries = load_development(root, allow_proposed=allow_proposed)
    protocol = json.loads((root / 'evaluation/v2/protocol.json').read_text(encoding='utf-8'))
    inputs = ['evaluation/v2/development.json', 'evaluation/v2/protocol.json',
              'src/sherlock_search/bm25.py', 'src/sherlock_search/v2_development.py']
    hashes = {name: hashlib.sha256((root / name).read_bytes()).hexdigest() for name in inputs}
    package = Path(__file__).resolve().parent
    for name in ('bm25.py', 'v2_development.py'):
        if hashlib.sha256((package / name).read_bytes()).hexdigest() != hashes['src/sherlock_search/' + name]:
            raise ValueError('Código v2 importado diverge da árvore informada.')
    paragraphs, corpus = prepare_corpus(raw_dir)
    report = compare_development(paragraphs, queries, protocol)
    if verify_preservation(root) != before:
        raise ValueError('Manifesto v1 alterado durante a execução.')
    if any(hashlib.sha256((root / name).read_bytes()).hexdigest() != expected for name, expected in hashes.items()):
        raise ValueError('Código ou entradas de desenvolvimento alterados durante a execução.')
    report.update(versions=versions, input_sha256=hashes, corpus_totals=corpus['totals'],
                  v1_preserved=True, final_v2_executed=False)
    return report


def validate_output(root: Path, output: Path) -> Path:
    output = output.resolve()
    if (not output.is_relative_to(root.resolve() / 'reports/v2') or output.suffix != '.json'
            or (output.exists() and (not output.is_file() or output.stat().st_nlink > 1))):
        raise ValueError('A saída deve ser um JSON próprio em reports/v2, sem sobrescrever insumos ou a v1.')
    return output


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path('.'))
    parser.add_argument('--raw-dir', type=Path, default=Path('data/raw'))
    parser.add_argument('--output', type=Path, default=Path('reports/v2/development.proposed.json'))
    parser.add_argument('--allow-proposed', action='store_true', help='Exploração explícita de rótulos ainda não aprovados.')
    args = parser.parse_args()
    root = args.root.resolve()
    try:
        output = validate_output(root, root / args.output)
        report = run_development(root, (root / args.raw_dir).resolve(), allow_proposed=args.allow_proposed)
        validate_output(root, output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    except (OSError, ValueError, KeyError, TypeError) as error:
        parser.error(str(error))
    print(f'Desenvolvimento v2: {report["query_count"]} consultas; rótulos {report["annotation_status"]}.')
    print('O teste reservado não foi carregado nem executado. Nenhum corte foi aplicado ao mecanismo distribuído.')
    for name in ('literal_v1', 'tfidf_v1', 'bm25_uncut', 'bm25_candidate'):
        row = report[name]
        print(f'{name}: hits conhecidos {row["positive_hits"]}/{row["positive_queries"]}; negativas com retorno {row["false_positive_queries"]}/{row["negative_queries"]}')


if __name__ == '__main__':
    main()
