"""Visualize known-reference positions from saved results, without running search."""
import argparse
import json
from pathlib import Path


def query_positions(report, methods):
    rows = [row for row in report['results'] if row['answerable']]
    positions = [
        [next((rank for rank, hit in enumerate(row[key][:5], 1)
               if hit['id'] in row['known_relevant_ids']), 0)
         for key, _ in methods]
        for row in rows
    ]
    return [row['id'] for row in rows], positions


def plot_positions(report, methods):
    import matplotlib.pyplot as plt
    from matplotlib.colors import BoundaryNorm, ListedColormap
    from matplotlib.patches import Patch

    ids, positions = query_positions(report, methods)
    if not ids:
        raise ValueError('No positive queries in saved report.')
    colors = ['#E9ECEF', '#184E62', '#31778A', '#6AA2AD', '#A3C5CB', '#D0E3E6']
    cmap = ListedColormap(colors)
    fig, ax = plt.subplots(figsize=(7.8, max(6, len(ids) * .37 + 1.7)), layout='constrained')
    ax.imshow(positions, cmap=cmap, norm=BoundaryNorm([-.5, .5, 1.5, 2.5, 3.5, 4.5, 5.5], cmap.N), aspect='auto')
    ax.set_xticks(range(len(methods)), [name for _, name in methods], fontsize=12)
    ax.xaxis.tick_top()
    ax.set_yticks(range(len(ids)), [f'Consulta {name.rsplit("-", 1)[-1]}' for name in ids])
    ax.tick_params(length=0, pad=8)
    for row, values in enumerate(positions):
        for column, rank in enumerate(values):
            ax.text(column, row, str(rank) if rank else '×', ha='center', va='center',
                    fontsize=12, color='white' if rank in (1, 2) else '#172B3A')
    ax.set_xticks([index - .5 for index in range(len(methods) + 1)], minor=True)
    ax.set_yticks([index - .5 for index in range(len(ids) + 1)], minor=True)
    ax.grid(which='minor', color='white', linewidth=2)
    ax.tick_params(which='minor', length=0)
    for spine in ax.spines.values():
        spine.set_visible(False)
    fig.suptitle('Em que posição apareceu a referência?', fontsize=16, x=.02, ha='left')
    ax.legend(handles=[Patch(facecolor=colors[1], label='1 a 5: posição da primeira referência conhecida'),
                       Patch(facecolor=colors[0], label='×: referência conhecida não encontrada no top 5')],
              loc='upper left', bbox_to_anchor=(0, -.02), frameon=False, fontsize=9)
    return fig


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('report', type=Path)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    report = json.loads(args.report.read_text(encoding='utf-8'))
    methods = [('literal_v1', 'Literal'), ('tfidf_v1', 'TF-IDF'), ('bm25', 'BM25')]
    fig = plot_positions(report, methods)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    for extension in ('png', 'svg'):
        fig.savefig(args.output.with_suffix('.' + extension), dpi=160, bbox_inches='tight', facecolor='white')


if __name__ == '__main__':
    main()
