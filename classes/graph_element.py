"""Two classes, Graph and GraphPlot, containing the values and formatting of the data to plot on graphs."""

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

    def add_plot(self, x, y, line_width=1.0, color="#000000"):
        """Creates and adds a :class:`classes.graph_element.GraphPlot` element to the :attr:`plots` attribute.

        .. versionadded:: 2.0

        Parameters
        ----------
        x: list(float) or numpy.array(float)
            An array of values to plot on the x axis.
        y: list(float) or numpy.array(float)
            An array of values to plot on the y axis.
        line_width: float, optional
            The width of the line to plot on the graph, in pixels. By default, the line width is 1 pixel.
        color: str, optional
            The hexadecimal value of the color of the line, prefixed by a number sign (``#``). By default, the color is
            black.
        """
        self.plots.append(GraphPlot(x, y, line_width, color))

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
            string += str(len(plot.x)) + "×" + str(len(plot.y)) + ", "
        string = string[:-2] + ")"
        return string


class GraphPlot(object):
    """Class containing the data of the x and y axis to plot in a graph, along with display settings such as line width
    and color.

    .. versionadded:: 2.0

    Parameters
    ----------
    x: list(float) or numpy.array(float)
        An array of values to plot on the x axis.
    y: list(float) or numpy.array(float)
        An array of values to plot on the y axis.
    line_width: float, optional
        The width of the line to plot on the graph, in pixels. By default, the line width is 1 pixel.
    color: str, optional
        The hexadecimal value of the color of the line, prefixed by a number sign (``#``). By default, the color is
        black.

    Attributes
    ----------
    x: list(float) or numpy.array(float)
        The array of values to plot on the x axis.
    y: list(float) or numpy.array(float)
        The array of values to plot on the y axis.
    line_width: float
        The width of the line to plot on the graph, in pixels.
    color: str
        The hexadecimal value of the color of the line, prefixed by a number sign (``#``).
    """

    def __init__(self, x, y, line_width=1.0, color="#000000"):
        self.x = x
        self.y = y
        self.line_width = line_width
        self.color = color
