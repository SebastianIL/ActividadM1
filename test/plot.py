import numpy as np
import matplotlib.pyplot as plt
from server import server, CrossroadModel

# Define the number of runs
num_runs = 100

# Create empty lists to store the data from each run
total_crashes_data = []
average_speed_red_data = []
average_speed_blue_data = []
average_speed_green_data = []

# Loop over the number of runs
for i in range(num_runs):
    # Create a new model instance
    model = CrossroadModel(N_cars=10, width=20, height=20)
    # Run the model for 100 steps
    for j in range(100):
        model.step()
    # Get the data from the model
    model_data = model.datacollector.get_model_vars_dataframe()
    # Append the data to the lists
    total_crashes_data.append(model_data["Total Crashes"])
    average_speed_red_data.append(model_data["Average Speed Red"])
    average_speed_blue_data.append(model_data["Average Speed Blue"])
    average_speed_green_data.append(model_data["Average Speed Green"])

# Convert the lists to numpy arrays
total_crashes_data = np.array(total_crashes_data)
average_speed_red_data = np.array(average_speed_red_data)
average_speed_blue_data = np.array(average_speed_blue_data)
average_speed_green_data = np.array(average_speed_green_data)

# Calculate the mean and standard deviation of the data
total_crashes_mean = np.mean(total_crashes_data, axis=0)
total_crashes_std = np.std(total_crashes_data, axis=0)
average_speed_red_mean = np.mean(average_speed_red_data, axis=0)
average_speed_red_std = np.std(average_speed_red_data, axis=0)
average_speed_blue_mean = np.mean(average_speed_blue_data, axis=0)
average_speed_blue_std = np.std(average_speed_blue_data, axis=0)
average_speed_green_mean = np.mean(average_speed_green_data, axis=0)
average_speed_green_std = np.std(average_speed_green_data, axis=0)

# Plot Total Crashes
plt.figure()
plt.errorbar(range(100), total_crashes_mean, yerr=total_crashes_std, label="Choques Totales")
plt.xlabel("Step")
plt.ylabel("Total Crashes")
plt.title("Choques totales x Step (en 100 corridas)")
plt.legend()
plt.show()

# Plot Average Speeds
plt.figure()
plt.errorbar(range(100), average_speed_red_mean, yerr=average_speed_red_std, label="Promedio agente irresponsable",color='red')
plt.errorbar(range(100), average_speed_blue_mean, yerr=average_speed_blue_std, label="Promedio agente responsable",color='blue')
plt.errorbar(range(100), average_speed_green_mean, yerr=average_speed_green_std, label="Promedio agente nuevo conductor",color='green')
plt.xlabel("Step")
plt.ylabel("Velocidad Promedio")
plt.title("Promedio de velocidad de diferentes agentes x Step (en 100 corridas)")
plt.legend()
plt.show()
