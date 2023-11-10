# Import the modules
from mesa import Agent, Model
from mesa.space import MultiGrid
from mesa.time import SimultaneousActivation
from mesa.datacollection import DataCollector
from mesa.visualization.modules import CanvasGrid,ChartModule
from mesa.visualization.ModularVisualization import ModularServer
import simpy
# Define the agent class for the car
class CarAgent(Agent):
    """An agent that represents a car."""

    def __init__(self, unique_id, model, lane, direction,color):
        super().__init__(unique_id, model)
        self.lane = lane 
        self.direction = direction 
        self.speed = 1
        self.velocity = self.speed
        # add some random factors to the velocity
        noise = self.random.normalvariate(0, 0.1) # generate a random noise from a normal distribution
        friction = 0.01 * self.speed # calculate a friction force proportional to the speed
        self.velocity = self.speed + noise - friction # update the velocity with the noise and the friction

        self.turn_choice = None 
        self.crashed = False  
        self.crash_count = 0  
        self.total_speed = 0  
        self.steps_taken = 0  
        self.color = color 
        # assign different speeds to different colors
        if self.color == "red":
            self.speed = 2 # red cars are faster
        elif self.color == "blue":
            self.speed = 1 # blue cars are normal
        elif self.color == "green":
            self.speed = 0.5 # green cars are slower
        self.start_time = self.model.schedule.time 
        self.average_speed = self.speed 
        if direction == 0: 
            x = 3 + lane
            y = self.random.randrange(10, 20)
        elif direction == 1: 
            x = self.random.randrange(0, 10)
            y = 3 + lane
        elif direction == 2: 
            x = 16 - lane
            y = self.random.randrange(0, 10)
        elif direction == 3: 
            x = self.random.randrange(10, 20)
            y = 16 - lane

        self.model.grid.place_agent(self, (x, y))

    def move(self):
        if not self.crashed and self.pos is not None:
            
            x, y = self.pos
            next_x,next_y=x,y
            if next_x < 0: 
                next_x = 19 
            elif next_x > 19: 
                next_x = 0 
            if next_y < 0: 
                next_y = 19 
            elif next_y > 19: 
                next_y = 0 

            this_cell = self.model.grid.get_cell_list_contents([self.pos])
            next_cell = self.model.grid.get_cell_list_contents([(next_x, next_y)])
            next_cell_cars = [obj for obj in next_cell if isinstance(obj, CarAgent)]
            
            if self.color == "green":
                slow_prob = self.random.random()
                if slow_prob < 0.5:
                    if (next_x, next_y) in [(3, 4), (4, 3), (5, 6), (6, 5)]:
                        self.velocity = 0.5 
                stop_prob = self.random.random()
                if stop_prob < 0.1:
                    self.velocity = 0

            if self.color == "red": 
                ignore_prob = self.random.random()
                if ignore_prob < 0.1:
                    self.velocity = self.speed 
                    # add some random factors to the velocity
                    noise = self.random.normalvariate(0, 0.1) # generate a random noise from a normal distribution
                    friction = 0.01 * self.speed # calculate a friction force proportional to the speed
                    self.velocity = self.speed + noise - friction # update the velocity with the noise and the friction

                    self.model.grid.move_agent(self, (next_x, next_y))
                sidewalk_prob = self.random.random()
                if sidewalk_prob < 0.05:
                    if self.direction == 0 or self.direction == 2:
                        next_x = self.random.choice([0, 9])
                    else:
                        next_y = self.random.choice([0, 9])
                    self.model.grid.move_agent(self, (next_x, next_y))

            if next_cell_cars and any(car.unique_id != self.unique_id for car in next_cell_cars):
                self.crashed = True
                self.velocity = 0 # set the velocity to zero
                self.crash_count += 1  
                for car in next_cell_cars:
                    car.crashed = True
                    car.crash_count += 1  
            else:
                self.total_speed += self.velocity # use the velocity instead of the speed
                self.steps_taken += 1 # increment the steps taken only if the car is moving
                self.average_speed = self.total_speed / self.steps_taken # calculate the average speed
                self.model.grid.move_agent(self, (next_x, next_y))

            if self.direction == 0: 
                next_x = x
                next_y = y - self.velocity # use the velocity instead of the speed
            elif self.direction == 1: 
                next_x = x + self.velocity # use the velocity instead of the speed
                next_y = y
            elif self.direction == 2: 
                next_x = x
                next_y = y + self.velocity # use the velocity instead of the speed
            elif self.direction == 3: 
                next_x = x - self.velocity # use the velocity instead of the speed
                next_y = y

            if (next_x, next_y) in self.model.roads:
                if (next_x, next_y) in [(4, 4), (5, 4), (5, 5), (4, 5)]:
                    light = self.model.traffic_lights[self.direction][self.lane]
                    if light.state == "green":
                        if next_cell_cars and any(car.unique_id != self.unique_id for car in next_cell_cars):
                            self.crashed = True
                            for car in next_cell_cars:
                                car.crashed = True
                        else:
                            if next_cell_cars and any(car.unique_id != self.unique_id for car in next_cell_cars):
                                self.crashed = True
                                for car in next_cell_cars:
                                    car.crashed = True
                            else:
                                self.model.grid.move_agent(self, (next_x, next_y))
                    elif light.state == "yellow":
                        self.speed = 0.5

                        if next_cell_cars and any(car.unique_id != self.unique_id for car in next_cell_cars):
                            self.crashed = True
                            for car in next_cell_cars:
                                car.crashed = True
                        else:
                            self.model.grid.move_agent(self, (next_x, next_y))
                    else:
                        pass
                else:
                    if self.direction == 0 or self.direction == 2:
                        if next_x == x: 
                            
                            if next_cell_cars and any(car.unique_id != self.unique_id for car in next_cell_cars):
                                self.crashed = True
                            for car in next_cell_cars:
                                car.crashed = True
                            else:
                                self.model.grid.move_agent(self, (next_x, next_y))
                        else:

                            pass
                    elif self.direction == 1 or self.direction == 3:
                        if next_y == y: 
                            
                            if next_cell_cars and any(car.unique_id != self.unique_id for car in next_cell_cars):
                                self.crashed = True
                                for car in next_cell_cars:
                                    car.crashed = True
                            else:
                                self.model.grid.move_agent(self, (next_x, next_y))
                        else:
                            pass
            else:
                pass

    def turn(self):
        x, y = self.pos
        if x == 4 and y == 4: 
            if self.direction == 1: 
                if self.turn_choice == 0: 
                    self.direction = 0 
                elif self.turn_choice == 1: 
                    self.direction = 2 
            elif self.direction == 2: 
                if self.turn_choice == 0: 
                    self.direction = 1 
                elif self.turn_choice == 1: 
                    self.direction = 3 
        elif x == 5 and y == 4: 
            if self.direction == 2: 
                if self.turn_choice == 0: 
                    self.direction = 3 
                elif self.turn_choice == 1: 
                    self.direction = 1 
            elif self.direction == 3: 
                if self.turn_choice == 0: 
                    self.direction = 0 
                elif self.turn_choice == 1: 
                    self.direction = 2 
        elif x == 5 and y == 5: 
            if self.direction == 0: 
                if self.turn_choice == 0: 
                    self.direction = 3 
                elif self.turn_choice == 1: 
                    self.direction = 1 
            elif self.direction == 3: 
                if self.turn_choice == 0: 
                    self.direction = 2 
                elif self.turn_choice == 1: 
                    self.direction = 0 
        elif x == 4 and y == 5: 
            if self.direction == 0: 
                if self.turn_choice == 0: 
                    self.direction = 1 
                elif self.turn_choice == 1: 
                    self.direction = 3 
            elif self.direction == 1: 
                if self.turn_choice == 0: 
                    self.direction = 2 
                elif self.turn_choice == 1: 
                    self.direction = 0 

    def step(self):
        self.move()
        self.turn()

class TrafficLightAgent(Agent):
    """An agent that represents a traffic light."""

    def __init__(self, unique_id, model, direction, lane, state):
        super().__init__(unique_id, model)
        self.direction = direction # The direction that the traffic light faces (0: up, 1: right, 2: down, 3: left)
        self.lane = lane # The lane that the traffic light controls (0: left, 1: right, 2: middle, 3: rightmost)
        self.state = state # The state of the traffic light ("red", "green", or "yellow")
        self.yellow_time = 5 # The duration of the yellow phase in seconds

    def switch(self):
        # Switch the state of the traffic light
        if self.state == "red":
            self.state = "green"
        elif self.state == "green":
            self.state = "yellow"
        else:
            self.state = "red"



# Define the model class for the crossroad
class CrossroadModel(Model):
    """A model with some number of cars and a crossroad."""

    def __init__(self, N_cars, width, height):
        self.num_cars = N_cars
        self.grid = MultiGrid(20, 20, True)
        self.schedule = SimultaneousActivation(self)

        # Create the road layout
        self.roads = [] # A list of road cells
        self.create_road_layout()

        # Create cars
        for i in range(self.num_cars):
            # Choose a random lane and direction
            lane = self.random.choice([0, 1])
            direction = self.random.choice([0, 1, 2, 3])
            # Choose a random turn
            turn = self.random.choice([None, 0, 1])
            # Create a car agent
            color = self.random.choice(["blue", "green", "red"])
            a = CarAgent(i, self, lane, direction, color)
            self.schedule.add(a)
            # Add the car to a valid grid cell based on the lane and direction
            if direction == 0: 
                x = 2 + lane
                y = self.random.randrange(6, 10)
            elif direction == 1: 
                x = self.random.randrange(0, 4)
                y = 2 + lane
            elif direction == 2: 
                x = 6 + lane
                y = self.random.randrange(0, 4)
            elif direction == 3: 
                x = self.random.randrange(6, 10)
                y = 6 + lane
            self.grid.place_agent(a, (x, y))

        self.traffic_lights = [] # A list of traffic lights
        for i in range(4): # For each direction
            lights = [] # A list of traffic lights for the same direction
            for j in range(4): # For each lane
                # Create a traffic light agent
                a = TrafficLightAgent((i, j), self, i, j, "red")
                self.schedule.add(a)
                # Add the traffic light to the corresponding grid cell
                if i == 0: 
                    x = 1 + j
                    y = 3
                elif i == 1: 
                    x = 6
                    y = 1 + j
                elif i == 2: 
                    x = 8 - j
                    y = 6
                elif i == 3: # Left
                    x = 3
                    y = 8 - j
                self.grid.place_agent(a, (x, y))
                # Append the traffic light to the list
                lights.append(a)
            # Append the list of traffic lights to the list
            self.traffic_lights.append(lights)

        # Define the traffic light cycle and phase
        self.cycle = 120 # 
        self.phase = 60 # The duration of the green phase in seconds
        self.yellow_time = 5 # The duration of the yellow phase in seconds
        # Start the traffic light controller
        self.env = simpy.Environment() # Create a simpy environment
        self.env.process(self.control_traffic_lights()) # Start the process of controlling the traffic lights
        self.env.run(until=self.cycle) # Run the simulation for one cycle

        self.datacollector = DataCollector(
            model_reporters={
                "Total Crashes": self.calculate_total_crashes,
                "Average Speed Red": self.calculate_average_speed_red, # add a new function for the red cars
                "Average Speed Blue": self.calculate_average_speed_blue, # add a new function for the blue cars
                "Average Speed Green": self.calculate_average_speed_green, # add a new function for the green cars
            },
            agent_reporters={
                "Crashes": lambda a: getattr(a, 'crash_count', 0),
                "Total Distance": lambda a: getattr(a, 'total_distance', 0),
                "Average Speed": lambda a: getattr(a, 'average_speed', 0) if isinstance(a, CarAgent) else None
            }
        )


    
    def calculate_total_crashes(self):
        return sum([car.crash_count for car in self.schedule.agents if isinstance(car, CarAgent)])

    def calculate_average_speed(self):
        total_average_speed = sum([car.average_speed for car in self.schedule.agents if isinstance(car, CarAgent)])
        car_count = sum([1 for car in self.schedule.agents if isinstance(car, CarAgent)])
        return total_average_speed / car_count if car_count else 0
    
    def calculate_average_speed_red(self):
        # calculate the average speed of the red cars
        total_average_speed_red = sum([car.average_speed for car in self.schedule.agents if isinstance(car, CarAgent) and car.color == "red"])
        car_count_red = sum([1 for car in self.schedule.agents if isinstance(car, CarAgent) and car.color == "red"])
        return total_average_speed_red / car_count_red if car_count_red else 0

    def calculate_average_speed_blue(self):
        # calculate the average speed of the blue cars
        total_average_speed_blue = sum([car.average_speed for car in self.schedule.agents if isinstance(car, CarAgent) and car.color == "blue"])
        car_count_blue = sum([1 for car in self.schedule.agents if isinstance(car, CarAgent) and car.color == "blue"])
        return total_average_speed_blue / car_count_blue if car_count_blue else 0

    def calculate_average_speed_green(self):
        # calculate the average speed of the green cars
        total_average_speed_green = sum([car.average_speed for car in self.schedule.agents if isinstance(car, CarAgent) and car.color == "green"])
        car_count_green = sum([1 for car in self.schedule.agents if isinstance(car, CarAgent) and car.color == "green"])
        return total_average_speed_green / car_count_green if car_count_green else 0



    def create_road_layout(self):
        # create a horizontal road
        for x in range(20):
            for y in [3, 4, 5, 6, 13, 14, 15, 16]: # increase the number of cells in the y direction
                self.roads.append((x, y))
                a = Agent((x, y), self)
                self.grid.place_agent(a, (x, y))
        # create a vertical road
        for x in [3, 4, 5, 6, 13, 14, 15, 16]: # increase the number of cells in the x direction
            for y in range(20):
                self.roads.append((x, y))
                a = Agent((x, y), self)
                self.grid.place_agent(a, (x, y))
        # create a vertical road
        for x in [3, 4, 5, 6, 13, 14, 15, 16]:
            for y in range(20):
                self.roads.append((x, y))
                a = Agent((x, y), self)
                self.grid.place_agent(a, (x, y))
        # create a vertical road
        for x in [3, 4, 5, 6, 13, 14, 15, 16]:
            for y in range(20):
                self.roads.append((x, y))
                a = Agent((x, y), self)
                self.grid.place_agent(a, (x, y))





    def control_traffic_lights(self):
        for i in range(4):
            for j in range(2):
                if i == 0:
                    self.traffic_lights[i][j].state = "green"
                else:
                    self.traffic_lights[i][j].state = "red"

        while True:
            yield self.env.timeout(self.phase)

            for i in range(4):
                for j in range(2):
                    self.traffic_lights[i][j].switch()

            yield self.env.timeout(self.yellow_time)

            for i in range(4):
                for j in range(2):
                    self.traffic_lights[i][j].switch()

            yield self.env.timeout(self.cycle - self.phase - self.yellow_time)

            for i in range(4):
                for j in range(2):
                    self.traffic_lights[i][j].switch()

    def respond_to_traffic_light(self):
        x, y = self.pos

        # Get the state of the traffic light in the current cell.
        traffic_light_state = self.model.grid.get_cell_object_at((x, y)).state

        # Take appropriate action based on the traffic light state.
        if traffic_light_state == "green":
            self.move()
        elif traffic_light_state == "yellow":
            self.speed = 0.5
            self.move()
        else:
            pass
    


    def step(self):
        self.schedule.step()
        self.datacollector.collect(self)





def agent_portrayal(agent):
    # Define the portrayal for the car agent
    if type(agent) is CarAgent:
        color = "red" if agent.crashed else "blue"
        portrayal = {"Shape": "circle",
                     "Filled": "true",
                     "Layer": 1,
                     "r": 0.5}
        # Add a conditional statement to check the crashed attribute
        if agent.crashed:
            # Change the color to red
            portrayal["Color"] = "black"
            # Add a text or an image to indicate the crash
            portrayal["Text"] = "Crash!"
        else:
            # Keep the color as blue
            portrayal["Color"] = agent.color

    else:
        portrayal = {"Shape": "rect",
                     "Filled": "true",
                     "Layer": 0,
                     "Color": "gray",
                     "w": 1,
                     "h": 1}
    return portrayal

grid = CanvasGrid(agent_portrayal, 20, 20, 500, 500)

model_params = {
    "N_cars": 10,
    "width": 10,
    "height": 10
}

total_crashes_chart = ChartModule([{"Label":"Total Crashes","Color":"Black"}],data_collector_name='datacollector')
average_speed_chart = ChartModule([{"Label":"Average Speed Red","Color":"Red", "ErrorBar":True}, # add an error bar for the red cars
                                   {"Label":"Average Speed Blue","Color":"Blue", "ErrorBar":True}, # add an error bar for the blue cars
                                   {"Label":"Average Speed Green","Color":"Green", "ErrorBar":True}], # add an error bar for the green cars
                                  data_collector_name='datacollector')


server = ModularServer(CrossroadModel,
                       [grid,total_crashes_chart,average_speed_chart],
                       "Crossroad Model",
                       model_params)
