# import airsim
import time

duration = 20
# client = airsim.MultirotorClient()

path_of_file = "run_0.OBJ"

init_time = time.time()
with open(path_of_file, "r") as run:
    lines = run.readlines()

file = []
for line in lines:
    file.append(line.rstrip())

lista_com_valores = []

for line in file:
    if line.startswith("v"):
        lista_com_valores.append(line[2:])

list_of_lists = [valor.split() for valor in lista_com_valores]

converted_list = [[float(value) for value in sublist] for sublist in list_of_lists]

end_time = time.time()

print(f"Total time: {(end_time - init_time)*1e3} ms")

for i in range(len(converted_list)):
    client.simRunConsoleCommand(
        f"ke * plot_raytrace {lista_com_valores[i]} {lista_com_valores[i+1]} {duration}"
    )

"""for i in range(len(converted_list)):
    client.simRunConsoleCommand(f'ke * plot_raytrace {lista_com_valores[i]} {lista_com_valores[i+1]} {duration}')
"""
