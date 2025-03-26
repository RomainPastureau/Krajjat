"""Tests the GraphElement functions from the toolbox."""

import unittest
import numpy as np

from krajjat.classes import GraphPlot


class TestsGraphElements(unittest.TestCase):

    def test_graph_plot_init(self):
        graph_plot = GraphPlot(np.linspace(0, 100, 101), np.linspace(0, 100, 101))
        assert np.allclose(graph_plot.x, np.linspace(0, 100, 101))
        assert np.allclose(graph_plot.y, np.linspace(0, 100, 101))
        assert graph_plot.sd is None
        assert graph_plot.line_width == 1.0
        assert graph_plot.color == "#000000"
        assert graph_plot.label is None

        graph_plot = GraphPlot(np.arange(0, 101), np.arange(0, 101), np.ones(101), 4.0, "red", "test")
        assert np.allclose(graph_plot.x, np.arange(0, 101))
        assert np.allclose(graph_plot.y, np.arange(0, 101))
        assert np.allclose(graph_plot.sd, np.ones(101))
        assert graph_plot.line_width == 4.0
        assert graph_plot.color == "red"
        assert graph_plot.label == "test"

        self.assertRaises(AssertionError, GraphPlot, [0, 1, 2], [0, 1, 2], "error", "red", "test")
        self.assertRaises(AssertionError, GraphPlot, [0, 1, 2], [0, 1, 2], 1.0, "red", "error")

    def test_graph_plot_get_extrema(self):
        graph_plot = GraphPlot(np.linspace(0, 100, 101), np.linspace(0, 100, 101))
        assert graph_plot.get_extrema() == (0, 100)

        graph_plot = GraphPlot(np.arange(0, 101), np.arange(0, 101))
        assert graph_plot.get_extrema(50, 75) == (50, 75)

        graph_plot = GraphPlot(np.arange(101, 0, -1), np.arange(101, 0, -1))
        assert graph_plot.get_extrema(50, 75) == (50, 75)