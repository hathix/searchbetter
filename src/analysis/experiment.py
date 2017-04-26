import pandas as pd
import plots
import stats

import matplotlib.pyplot as plt

def term_stats(term, engine, rewriters):
    ans = [num_results(engine, term, rw) for rw in rewriters]
    ans = [term] + ans
    return ans


def num_results(engine, term, rw):
    engine.set_rewriter(rw)
    results = engine.search(term)
    num_results = len(results)
    return num_results


def generate_stats(engine, slug, rewriters, filename, cached=False):
    cache_file = '../tmp/queries-%s.csv' % slug
    if cached:
        # rehydrate the cached version
        df = pd.read_csv(cache_file, index_col=0)
    else:
        with open(filename, 'r') as f:
            # read terms but chop the newlines at the end of each line
            terms = [line.rstrip('\n') for line in f]
            data = [term_stats(term, engine, rewriters) for term in terms]

        df = pd.DataFrame(columns=["term","control","wiki","word2vec"], data=data)
        # store it for future reference
        df.to_csv(cache_file)

    return df


def display_engine_plots(slug, colors, dfs):

    # plots.plotly_scatter(control_hits, wiki_hits, w2v_hits)

    # mpl
    fig, ax = plt.subplots(3,2, figsize=(12,12))

    for i, row in enumerate(ax):
        df = dfs[i]

        # filter out the crazy big stuff
        # TODO make this dynamic so it doesn't auto cut off bad stuff
        # fdf = df[df['control'] <= 50]
        fdf = df

        control_hits = list(fdf['control'])
        wiki_hits = list(fdf['wiki'])
        w2v_hits = list(fdf['word2vec'])

        for j, cell in enumerate(row):
            color = colors[j]
            # show wiki, w2v on diff sides
            ys = [wiki_hits, w2v_hits][j]
            plots.matplotlib_scatter(cell, control_hits, ys, color)

    # display
    fig.tight_layout()
