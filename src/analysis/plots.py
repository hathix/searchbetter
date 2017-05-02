import numpy as np
import scipy

import plotly
import plotly.graph_objs as go
import plotly.offline as py
py.init_notebook_mode()

import matplotlib.pyplot as plt

import stats

def plotSeriesWithRegression(xs, ys, name, color):
    """
    Returns a list of traces:
        - A scatter plots of ys
        - A linear regression of ys
    """
    # setting legend group lets user toggle the series AND its
    # line of best fit together
    legendgroup_name = '%s group' % name

    # plot points
    traceScatter = go.Scattergl(
        x = xs,
        y = ys,
        mode = 'markers',
        name = name,
        legendgroup = legendgroup_name,
        marker = dict(
            color = color,
            opacity = 0.5,
            size = 12,
            line = dict(
                width = 2,
                color = 'rgb(0, 0, 0)'
            )
        )
    )

    # plot line of best fit
    slope, intercept, r_value, p_value, std_err = scipy.stats.linregress(xs, ys)
    line_of_best_fit = np.poly1d([slope, intercept])
    r_squared = r_value ** 2

    # to show line of best fit
    # y = %.2fx + %.2f, r^2 = %.2f' % (slope, intercept, r_squared),

    traceRegression = go.Scattergl(
        x = np.unique(xs),
        y = line_of_best_fit(np.unique(xs)),
        mode = 'lines',
        name = name + ' linear regression',
        legendgroup = legendgroup_name,
        hoverinfo = 'text+name',
        line = dict(
            color = color
        )
    )

    return [traceScatter, traceRegression]


def plotly_scatter(control_hits, wiki_hits, w2v_hits):
    # reference: https://plot.ly/python/reference/#scattergl

    traceControl = go.Scattergl(
        x = control_hits,
        y = control_hits,
        mode = 'lines',
        name = 'Control (no rewriting)',
        hoverinfo = 'text+name',
        line = dict(
            color = color_strings[0]
        )
    )

    # plot wiki
    wikiTraces = plots.plotSeriesWithRegression(
        control_hits, wiki_hits, name='Wikipedia Categories', color=color_strings[1])
    w2vTraces = plots.plotSeriesWithRegression(
        control_hits, w2v_hits, name='Word2Vec', color=color_strings[2])

    plot = [traceControl] + wikiTraces + w2vTraces

    layout = go.Layout(
        title='Effect of query rewriting on search engine hits (edX)',
        xaxis=dict(
            title='# hits before rewriting'
        ),
        yaxis=dict(
            title='# hits after rewriting'
        )
    )

    fig = go.Figure(data=plot, layout=layout)

    # Plot and embed in ipython notebook!
    py.iplot(fig)


def matplotlib_scatter(subplot, xs, ys, max_x, max_y, x_label, y_label, title, rewriter_name, color):
    # scatter plot
    scatter = subplot.scatter(x=xs, y=ys, alpha=0.5, c=color)

    # line of best fit
    slope, intercept, r_value, p_value, std_err = scipy.stats.linregress(xs, ys)
    line_of_best_fit = np.poly1d([slope, intercept])
    r_squared = r_value ** 2
    regression, = subplot.plot(np.unique(xs), line_of_best_fit(np.unique(xs)), c=color)
    print("y = %.2fx + %.2f, r^2 = %.2f" % (slope, intercept, r_squared))

    # control line
    control, = subplot.plot(np.unique(xs), np.unique(xs), c="#444444", linestyle="dashed")

    subplot.set_xlim(0, max_x)
    subplot.set_ylim(0, max_y)

    subplot.set_xlabel(x_label)
    subplot.set_ylabel(y_label)

    subplot.set_title(title)

    subplot.legend(
        handles=[scatter, regression, control],
        labels=[rewriter_name, "Regression for {}".format(rewriter_name), "Control"]
    )

    return subplot



def summary_bar_chart(df, engine_name):
    # BAR CHARTS
    # more stats
    rewriter_names =[
        'control',
        'wiki',
        'word2vec'
    ]

    # filter out any rows where there are always zero hits
    fdf = df[(df['control'] > 0) | (df['wiki'] > 0) | (df['word2vec'] > 0)]
    fdf = fdf.reset_index(drop=True)

    print stats.summary_of_frame(fdf)

    # series containing # of hits for each search term
    data_series = [fdf[name] for name in rewriter_names]
    average_hits = [s.mean() for s in data_series]

    # now filter on just those terms where the control gives nothing

    df_where_no_hits = fdf[fdf['control'] == 0]
    data_series_zero = [df_where_no_hits[name] for name in rewriter_names]
    average_hits_zero = [s.mean() for s in data_series_zero]

    print stats.summary_of_frame(df_where_no_hits)


    # bar chart of hits

    # first trace: all search terms
    rewriter_fancy_names = [
        'Control (no rewriting)',
        'Wikipedia Categories',
        'Word2Vec'
    ]

    traceAllTerms = go.Bar(
        x=rewriter_fancy_names,
        y=average_hits,
        name='All terms'
    )
    traceJustMisses = go.Bar(
        x=rewriter_fancy_names,
        y=average_hits_zero,
        # for some reason, when you export the image, it chops off the
        # trailing letters of this label. so let's pad it with spaces to
        # save the text
        name='Terms with no hits by default  '
    )

    traces = [traceAllTerms, traceJustMisses]
    layout = go.Layout(
        barmode='group',
        title='Average hits per rewriter (%s)' % engine_name,
        xaxis=dict(
            title='Query rewriter'
        ),
        yaxis=dict(
            title='Average # hits'
        ),
        legend=dict(
            # center the legend and put it below the graph
            x=0.35,
            # when you export plot to image, for some reason it moves the
            # legend up no matter what you do. so we need to exaggerate how
            # far down the legend is here.
            y=-0.7
        )
    )

    fig = go.Figure(data=traces, layout=layout)

    return fig
