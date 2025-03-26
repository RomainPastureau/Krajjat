"""Two classes, Graph and GraphPlot, containing the values and formatting of the data to plot on graphs."""
import numpy as np


class Graph(object):
    """Class containing multiple plots (each being a :class:`classes.graph_element.GraphPlot`) to display on the same
    graph.

    .. versionadded:: 2.0

    Attributes
    ----------
    plots: list(GraphPlot)
        A list of GraphPlot elements to display on the same graph.
    """

    def __init__(self):
        self.plots = []

    def add_plot(self, x, y, sd=None, line_width=1.0, color="#000000", label=None):
        """Creates and adds a :class:`classes.graph_element.GraphPlot` element to the :attr:`plots` attribute.

        .. versionadded:: 2.0

        Parameters
        ----------
        x: list(float) or numpy.array(float)
            An array of values to plot on the x-axis.
        y: list(float) or numpy.array(float)
            An array of values to plot on the y-axis.
        sd: list(float), numpy.array(float), or None, optional
            A list containing the standard deviations of x.
        line_width: float, optional
            The width of the line to plot on the graph, in pixels. By default, the line width is 1 pixel.
        color: str, optional
            The hexadecimal value of the color of the line, prefixed by a number sign (``#``). By default, the color is
            black.
        label: str, optional
            The label of the series.
        """
        self.plots.append(GraphPlot(x, y, sd, line_width, color, label))

    def add_graph_plot(self, graph_plot):
        """Adds an already created :class:`classes.graph_element.GraphPlot` element to the :attr:`plots` attribute.

        .. versionadded:: 2.0

        Parameters
        ----------
        graph_plot: GraphPlot
            A GraphPlot element.
        """
        self.plots.append(graph_plot)

    def __repr__(self):
        """Returns a textual representation of the content of the Graph element, indicating the number of plots and
        their respective dimensions.

        .. versionadded:: 2.0

        Returns
        -------
        str
            A string representation of the content of the Graph element, indicating the number of plots and
            their respective dimensions.
        """
        if len(self.plots) == 1:
            string = str(len(self.plots)) + " plot ("
        else:
            string = str(len(self.plots))+" plots ("
        for plot in self.plots:
            string += f"{plot.label} · {len(plot.x)} × {len(plot.y)}"
            if plot.sd is not None:
                string += " (with SD)"
            string += ", "
        string = string[:-2] + ")"

        return string


class GraphPlot(object):
    """Class containing the data of the x and y-axis to plot in a graph, along with display settings such as line width
    and color.

    .. versionadded:: 2.0

    Parameters
    ----------
    x: list(float) or numpy.array(float)
        An array of values to plot on the x-axis.
    y: list(float) or numpy.array(float)
        An array of values to plot on the y-axis.
    sd: list(float), numpy.array(float), or None, optional
        A list containing the standard deviations of x.
    line_width: float, optional
        The width of the line to plot on the graph, in pixels. By default, the line width is 1 pixel.
    color: str, optional
        The hexadecimal value of the color of the line, prefixed by a number sign (``#``). By default, the color is
        black.
    label: str, optional
        The label of the series.

    Attributes
    ----------
    x: numpy.array(float)
        The array of values to plot on the x-axis.
    y: numpy.array(float)
        The array of values to plot on the y-axis.
    sd: numpy.array(float), or None, optional
        The array containing the standard deviations of x.
    line_width: float
        The width of the line to plot on the graph, in pixels.
    color: str
        The hexadecimal value of the color of the line, prefixed by a number sign (``#``).
    label: str, optional
        The label of the series.
    """

    def __init__(self, x, y, sd=None, line_width=1.0, color="#000000", label=None):
        self.x = np.array(x)
        self.y = np.array(y)
        self.sd = None
        if sd is not None:
            self.sd = np.array(sd)
        assert isinstance(line_width, (int, float))
        self.line_width = line_width
        self.color = color
        assert isinstance(label, (str, type(None)))
        self.label = label

    def get_extrema(self, x_min=None, x_max=None):
        """Returns the min and the max of the y array, given the x limits.

        .. versionadded:: 2.0

        Parameters
        ----------
        x_min: int|float, optional
            The minimum value of the x-axis. If None, sets the x_min to the minimum value of the x array.

        x_max: int|float, optional
            The maximum value of the x-axis. If None, sets the x_max to the maximum value of the x array.

        Returns
        -------
        int|float, int|float
            The minimum and maximum values of the y array, given the x limits.
        """
        if x_min is None:
            x_min = np.min(self.x)
        if x_max is None:
            x_max = np.max(self.x)
        return (np.min(self.y[np.where((self.x >= x_min) & (self.x <= x_max))]),
                np.max(self.y[np.where((self.x >= x_min) & (self.x <= x_max))]))