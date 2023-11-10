import numpy as np
import matplotlib.pyplot as plt
from model import transito, coche, peaton

resultados = []
choques = []
atropellados = []

# Ejecuta la simulación con un número creciente de aspiradoras
for num_coches in range(8, 21):
    pasos = []
    accidentes = []
    peatonales = []

    # Repite la simulación 100 veces
    for _ in range(100):
        # Crea una nueva instancia del modelo
        modelo = transito(num_agents=num_coches, num_peatones=15, width=20, height=20)
        while modelo.running:
            modelo.step()
        pasos.append(modelo.schedule.steps)
        accidentes.append(modelo.acc)
        peatonales.append(modelo.atropellados)
    # Almacena el número promedio de pasos
    resultados.append(sum(pasos) / len(pasos))
    choques.append(sum(accidentes) / len(accidentes))
    atropellados.append(sum(peatonales) / len(peatonales))

resultados = np.array(resultados)
choques = np.array(choques)
atropellados = np.array(atropellados)

resultados_std = np.std(resultados)
atropellados_std = np.std(atropellados)
# Grafica los resultados
plt.errorbar(range(8, 21), resultados, yerr=resultados_std)
plt.title('Pasos necesarios para que todos los coches choquen')
plt.suptitle('(100 repeticiones 15 peatones)')
plt.xlabel('Número de coches')
plt.ylabel('Número promedio de pasos')
plt.show()

plt.errorbar(range(8, 21), atropellados, yerr=atropellados_std)
plt.title('peatones atropellados vs cantidad de vehiculos')
plt.suptitle('(100 repeticiones 15 peatones)')
plt.xlabel('Número de coches')
plt.ylabel('Número promedio de atropellados')
plt.show()
