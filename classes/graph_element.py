class Graph(object):

    def __init__(self):
        self.plots = []

    def add_plot(self, x, y, line_width=1.0, color="#000000"):
        self.plots.append(GraphPlot(x, y, line_width, color))

    def __repr__(self):
        if len(self.plots) == 1:
            string = str(len(self.plots)) + " plot ("
        else:
            string = str(len(self.plots))+" plots ("
        for plot in self.plots:
            string += str(len(plot.x)) + "×" + str(len(plot.y)) + ", "
        string = string[:-2] + ")"
        return string


class GraphPlot(object):

    def __init__(self, x, y, line_width=1.0, color="#000000"):
        self.x = x
        self.y = y
        self.line_width = line_width
        self.color = color
