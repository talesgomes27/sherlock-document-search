"""Export the fixed v2 final comparison without recomputing retrieval."""

import json
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter


ROOT = Path(__file__).resolve().parents[1]


def main():
    report = json.loads((ROOT / 'reports/v2/final.json').read_text(encoding='utf-8'))
    assert report['split'] == 'v2_final' and report['query_count'] == 24
    assert report['final_v2_executed'] is True
    methods = [('literal_v1', 'Literal', '#23465D'), ('tfidf_v1', 'TF-IDF', '#B96A2A'), ('bm25', 'BM25', '#2D6477')]
    panels = [('known_hit_at_5', 'positive_hits', 'positive_queries', 18,
               'Consultas com referência no top 5', 'Maior é melhor · 18 consultas positivas'),
              ('false_positive_rate', 'false_positive_queries', 'negative_queries', 6,
               'Consultas sem resposta com retorno', 'Menor é melhor · 6 consultas negativas')]
    plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 11,
                         'axes.spines.top': False, 'axes.spines.right': False})
    fig, axes = plt.subplots(1, 2, figsize=(12, 5), layout='constrained')
    for ax, (metric, count, total, denominator, title, subtitle) in zip(axes, panels):
        values = [report['methods'][key][metric] for key, label, color in methods]
        bars = ax.barh([label for key, label, color in methods], values,
                       color=[color for key, label, color in methods], height=.55)
        ax.invert_yaxis()
        ax.set_xlim(0, 1)
        ax.set_xticks([0, .25, .5, .75, 1])
        ax.xaxis.set_major_formatter(PercentFormatter(1))
        ax.set_title(title + '\n' + subtitle, loc='left', fontsize=12, pad=18)
        ax.set_xlabel('Percentual de consultas')
        ax.grid(axis='x', alpha=.15)
        ax.set_axisbelow(True)
        for bar, (key, label, color), value in zip(bars, methods, values):
            row = report['methods'][key]
            assert row[total] == denominator and abs(value - row[count]/denominator) < 1e-12
            text = f'{row[count]}/{denominator} · {value:.1%}'.replace('.0%', '%').replace('.', ',')
            inside = value > .8
            ax.text(value-.03 if inside else value+.03, bar.get_y()+bar.get_height()/2, text,
                    va='center', ha='right' if inside else 'left', color='white' if inside else '#172B3A')
    fig.suptitle('V2: mais consultas com referência; abstenção ainda sem solução', fontsize=16)
    output = ROOT / 'reports/v2/figures'
    output.mkdir(parents=True, exist_ok=True)
    for extension in ('png', 'svg'):
        fig.savefig(output / f'final_comparison.{extension}', dpi=160, bbox_inches='tight', facecolor='white')
    svg = output / 'final_comparison.svg'
    svg.write_text('\n'.join(line.rstrip() for line in svg.read_text(encoding='utf-8').splitlines()) + '\n', encoding='utf-8')
    plt.close(fig)
    print('Gráficos exportados do relatório final; nenhuma busca foi executada.')


if __name__ == '__main__':
    main()
