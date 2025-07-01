# ranking.py
import csv
import os

ARCHIVO_RANKING = 'ranking.csv'

def guardar_ranking(nombre_jugador, tiempo_juego, movimientos):
    nueva_entrada = [nombre_jugador, tiempo_juego, movimientos]

    with open(ARCHIVO_RANKING, 'a', newline='') as file:
        writer = csv.writer(file)

        if file.tell() == 0:
            writer.writerow(['Nombre', 'Tiempo (segundos)', 'Movimientos'])

        writer.writerow(nueva_entrada)

    print(f"Ranking guardado: {nombre_jugador}, {tiempo_juego}, {movimientos}")


def cargar_ranking():
    ranking_data = []

    if not os.path.exists(ARCHIVO_RANKING):
        return ranking_data

    file = open(ARCHIVO_RANKING, 'r', newline='')
    reader = csv.reader(file)
    todas_las_filas_csv = list(reader)
    file.close()

    if not todas_las_filas_csv:
        return ranking_data

    lineas_de_datos = todas_las_filas_csv[1:]

    for fila_datos in lineas_de_datos:
        if len(fila_datos) == 3:
            nombre = fila_datos[0]
            tiempo = int(fila_datos[1])
            movimientos = int(fila_datos[2])

            ranking_data.append({
                'Nombre': nombre,
                'Tiempo (segundos)': tiempo,
                'Movimientos': movimientos
            })
    ranking_data.sort(key=lambda x: (x['Tiempo (segundos)'], x['Movimientos']))

    return ranking_data