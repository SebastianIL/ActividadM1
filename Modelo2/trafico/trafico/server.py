"""
Configure visualization elements and instantiate a server
"""

from .model import transito, coche, calle, banqueta, peaton  # noqa

import mesa


def vista_general(agent):
    if agent is None:
        return

    portrayal = {
        "Shape": "rect",
        "Filled": "true",
        "Layer": 0,
        "w": 0.5,
        "h": 0.5,
        "Color": "Blue",
    }

    if isinstance(agent, calle):
        portrayal["Color"] = "Black"
        portrayal["w"] = 1
        portrayal["h"] = 1

    elif isinstance(agent, banqueta):
        portrayal["Color"] = "Grey"
        portrayal["w"] = 1
        portrayal["h"] = 1

    elif isinstance(agent, coche):
        portrayal["Color"] = "Blue"
        portrayal["Layer"] = 2

    elif isinstance(agent, peaton):
        portrayal["Color"] = "Green"
        portrayal["Layer"] = 2
        portrayal["Shape"] = "circle"
        portrayal["r"] = 0.3

    return portrayal


canvas_element = mesa.visualization.CanvasGrid(
    vista_general, 20, 20, 500, 500
)

choques_element = mesa.visualization.ChartModule([
    {"Label": "Choques", "Color": "Red"},
    {"Label": "Atropellados", "Color": "Blue"},
], data_collector_name='datacollector')


model_kwargs = {"num_agents": 4, "num_peatones": 15, "width": 20, "height": 20}

server = mesa.visualization.ModularServer(
    transito,
    [canvas_element, choques_element],
    "trafico",
    model_kwargs,
)
