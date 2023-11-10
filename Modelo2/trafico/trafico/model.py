import random

import mesa


class calle(mesa.Agent):
    def __int__(self, unique_id, model, direction):
        self.unique_id = unique_id
        self.direction = direction
        super().__init__(unique_id, model)

    def __str__(self):
        return "calle"

    def step(self):
        pass


class banqueta(mesa.Agent):
    def __int__(self, unique_id, model):
        self.unique_id = unique_id
        self.esquina = False
        super().__init__(unique_id, model)

    def step(self):
        pass


class peaton(mesa.Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.unique_id = unique_id
        self.atropellado = False

    def step(self):
        vecindario = self.model.grid.get_neighborhood(self.pos, include_center=True, moore=True)
        vecinos = self.model.grid.get_cell_list_contents(vecindario)
        vecinos_acera = [vecino for vecino in vecinos if isinstance(vecino, banqueta)]
        pos_acera = [vecino.pos for vecino in vecinos_acera]
        pos = random.choice(pos_acera)
        self.model.grid.move_agent(self, pos)


class coche(mesa.Agent):
    def __init__(self, unique_id, model):
        self.unique_id = unique_id
        self.prev = None
        self.chocado = False
        self.lane = 0
        super().__init__(unique_id, model)

    def step(self):

        pos = self.pos
        x, y = pos[0], pos[1]

        cell_list = self.model.grid.get_cell_list_contents(pos)
        other_cars = [agent for agent in cell_list if isinstance(agent, coche) and agent != self]
        peatones = [agent for agent in cell_list if isinstance(agent, peaton) and agent != self]

        if other_cars and not self.chocado:  # Sí hay otros coches, establecer chocado en True
            self.model.acc += 1

        if peatones and not self.chocado:
            self.model.atropellados += 1

        if not self.chocado:
            if other_cars:  # Sí hay otros coches, establecer chocado en True
                self.model.acc += 1
                self.chocado = True

            if peatones:
                self.model.atropellados += 1

            if cell_list[0].unique_id == 0:
                if self.prev == (pos[0], pos[1] + 1):
                    self.prev = pos
                    self.model.grid.move_agent(self, (x, y - 1))
                else:
                    self.prev = pos
                    self.model.grid.move_agent(self, (x + 1, y))
            elif cell_list[0].unique_id == 1:
                if self.prev == (pos[0] - 1, pos[1]):
                    self.prev = pos
                    self.model.grid.move_agent(self, (x + 1, y))
                else:
                    self.prev = pos
                    self.model.grid.move_agent(self, (x, y - 1))

            elif cell_list[0].unique_id == 2:
                op = random.choice([0, 1])
                if self.prev == (pos[0], pos[1] + 1):
                    if op == 0:
                        self.prev = pos
                        self.model.grid.move_agent(self, (x + 1, y))
                    elif op == 1:
                        self.prev = pos
                        self.model.grid.move_agent(self, (x, y - 1))
                else:
                    if op == 0:
                        self.prev = pos
                        self.model.grid.move_agent(self, (x + 1, y))
                    elif op == 1:
                        self.prev = pos
                        self.model.grid.move_agent(self, (x, y - 1))

            elif cell_list[0].unique_id == 3:
                op = random.choice([0, 1])
                if self.prev == (pos[0] - 1, pos[1]):
                    if op == 0:
                        self.prev = pos
                        self.model.grid.move_agent(self, (x + 1, y))
                    elif op == 1:
                        self.prev = pos
                        self.model.grid.move_agent(self, (x, y - 1))
                else:
                    if op == 0:
                        self.prev = pos
                        self.model.grid.move_agent(self, (x + 1, y))
                    elif op == 1:
                        self.prev = pos
                        self.model.grid.move_agent(self, (x, y - 1))


class transito(mesa.Model):
    """
    The model class holds the model-level attributes, manages the agents, and generally handles
    the global level of our model.

    There is only one model-level parameter: how many agents the model contains. When a new model
    is started, we want it to populate itself with the given number of agents.

    The scheduler is a special model component which controls the order in which agents are activated.
    """

    def __init__(self, num_agents, num_peatones, width, height):
        super().__init__()
        self.acc = 0
        self.atropellados = 0
        self.num_agents = num_agents
        self.num_peatones = num_peatones
        self.run = True
        self.schedule = mesa.time.RandomActivation(self)
        self.grid = mesa.space.MultiGrid(width=width, height=height, torus=True)
        calle_abajo = calle(0, self)
        calle_derecha = calle(1, self)
        calle_vueltaI = calle(2, self)
        calle_vueltaD = calle(3, self)
        self.schedule.add(calle_derecha)
        self.schedule.add(calle_abajo)
        self.schedule.add(calle_vueltaI)
        self.schedule.add(calle_vueltaD)

        for i in range(20):
            if i == 9:
                self.grid.place_agent(calle_vueltaD, (i, 10))
                self.grid.place_agent(calle_vueltaD, (9, i))

            elif i == 10:
                self.grid.place_agent(calle_vueltaI, (i, 9))
                self.grid.place_agent(calle_vueltaI, (i, 10))
            else:
                self.grid.place_agent(calle_derecha, (9, i))
                self.grid.place_agent(calle_derecha, (10, i))
                self.grid.place_agent(calle_abajo, (i, 9))
                self.grid.place_agent(calle_abajo, (i, 10))

        for i in range(20):
            acera = banqueta(4 + i, self)
            self.schedule.add(acera)
            self.grid.place_agent(acera, (i, 8))

        for i in range(20):
            acera = banqueta(24 + i, self)
            self.schedule.add(acera)
            self.grid.place_agent(acera, (8, i))

        for i in range(20):
            acera = banqueta(44 + i, self)
            self.schedule.add(acera)
            self.grid.place_agent(acera, (11, i))

        for i in range(20):
            acera = banqueta(64 + i, self)
            self.schedule.add(acera)
            self.grid.place_agent(acera, (i, 11))

        for i in range(self.num_agents):
            carro = coche(84 + i, self)
            self.schedule.add(carro)

            x, y = self.random_calle_position()
            self.grid.place_agent(carro, (x, y))

        for i in range(self.num_peatones):
            persona = peaton(num_agents + 104 + i, self)
            self.schedule.add(persona)

            x, y = self.random_acera_position()
            self.grid.place_agent(persona, (x, y))

        # example data collector
        self.datacollector = mesa.datacollection.DataCollector(
            model_reporters={
                "Choques": self.get_acc,
                "Atropellados": self.get_atropellados
            }
        )

        self.running = True
        self.datacollector.collect(self)

    def get_acc(self):
        return self.acc

    def get_atropellados(self):
        return self.atropellados

    def random_acera_position(self):
        acera_cells = []

        for x in range(self.grid.width):
            for y in range(self.grid.height):
                cell_list = self.grid.get_cell_list_contents([(x, y)])
                for cell in cell_list:
                    if isinstance(cell, banqueta):
                        acera_cells.append(cell.pos)

        if acera_cells:
            return self.random.choice(acera_cells)
        else:
            return None

    def random_calle_position(self):
        calle_cells = []

        for x in range(self.grid.width):
            for y in range(self.grid.height):
                cell_list = self.grid.get_cell_list_contents([(x, y)])
                if cell_list:
                    if cell_list[0].unique_id == 0 or cell_list[0].unique_id == 1:
                        calle_cells.append((x, y))

        if calle_cells:
            return self.random.choice(calle_cells)
        else:
            return None

    def step(self):
        self.datacollector.collect(self)
        self.schedule.step()

        if self.acc == self.num_agents * 2 and not self.run:
            self.running = False

        if self.acc == self.num_agents * 2:
            self.run = False
