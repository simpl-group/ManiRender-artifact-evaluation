# -*- coding: utf-8 -*-


import dash_cytoscape as cyto
from dash import Dash, html


class Canvas:
    def __init__(self, name):
        self.name = name
        self.app = Dash(name)
        self.nodes = []
        self.edges = []
        self.styles = []

    def update(self, nodes, edges, styles):
        """
        :param nodes: {'data': {'id': 'ca', 'label': 'Canada'}, 'classes': 'node'}
        :param edges: {'data': {'source': 'ca', 'target': 'on'}, 'classes': 'edge'}
        :param style:   {
                            'selector': 'edge',
                            'style': {
                                'source-arrow-color': 'red',
                                'source-arrow-shape': 'triangle',
                                'line-color': 'red'
                            }
                        },
        """
        self.nodes += nodes
        self.edges += edges
        self.styles += styles

    def plot(self):
        self.app.layout = html.Div([
            html.P(f"Lattice of {self.name}"),
            cyto.Cytoscape(
                id=f'cytoscape-{self.name}',
                elements=self.nodes + self.edges,
                layout={
                    'name': 'breadthfirst',
                    'roots': [self.nodes[-1]['data']['id']]
                },
                style={'width': '800px', 'height': '800px'},
                stylesheet=self.styles,
            )
        ])

        self.app.run_server(debug=True)
