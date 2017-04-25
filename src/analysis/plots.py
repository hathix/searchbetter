import numpy as np

import plotly
import plotly.graph_objs as go
import plotly.offline as py

py.init_notebook_mode()

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
