import numpy as np
import scipy

import plotly
import plotly.graph_objs as go
import plotly.offline as py
py.init_notebook_mode()

import matplotlib.pyplot as plt

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


def matplotlib_scatter(subplot, xs, ys, max_x, max_y, x_label, y_label, color):
    # scatter plot
    subplot.scatter(x=xs, y=ys, alpha=0.5, c=color)

    # line of best fit
    subplot.plot(np.unique(xs), np.poly1d(np.polyfit(xs, ys, 1))(np.unique(xs)), c=color)

    # control line
    subplot.plot(np.unique(xs), np.unique(xs), c="#444444")

    # TODO make the maxes dynamic
    subplot.set_xlim(0, max_x)
    subplot.set_ylim(0, max_y)

    subplot.set_xlabel(x_label)
    subplot.set_ylabel(y_label)

    return subplot
