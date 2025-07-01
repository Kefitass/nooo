# cartas.py
import pygame
import random
from graficos import ANCHO, ALTO # Importamos ANCHO y ALTO para cálculos de posición/escala

# --- Constantes relacionadas con las cartas ---
ancho_carta = 90
alto_carta = 120
espacio_horizontal_entre_pilas = 11.6
espacio_vertical_dentro_pila = 30
inicio_x_pilas = 20
inicio_y_pilas = 160
mazo_reserva_x = inicio_x_pilas
mazo_reserva_y = 20
pila_descarte_x = mazo_reserva_x + ancho_carta + espacio_horizontal_entre_pilas
pila_descarte_y = 20
fundacion_final_x = ANCHO - 20
fundacion_x_base = fundacion_final_x - (4 * ancho_carta + 3 * espacio_horizontal_entre_pilas)
fundacion_y = 20

CARPETA_IMAGENES_CARTAS = 'cartas/'
NOMBRE_IMAGEN_REVERSO = "dorso carta.jpg"
IMAGEN_DORSO_CARTA_CARGADA = None
IMAGENES_CARTAS_CACHE = {}

# --- Funciones relacionadas con las cartas ---

def inicializar_recursos_graficos():
    """
    Carga la imagen del dorso de la carta y prepara el caché de imágenes.
    """
    global IMAGEN_DORSO_CARTA_CARGADA, IMAGENES_CARTAS_CACHE

    ruta_dorso = CARPETA_IMAGENES_CARTAS + NOMBRE_IMAGEN_REVERSO
    IMAGEN_DORSO_CARTA_CARGADA = pygame.image.load(ruta_dorso).convert_alpha()
    IMAGEN_DORSO_CARTA_CARGADA = pygame.transform.scale(IMAGEN_DORSO_CARTA_CARGADA, (ancho_carta, alto_carta))

    IMAGENES_CARTAS_CACHE = {}

def cargar_imagen_carta(valor, palo):
    """
    Carga y escala una imagen de carta específica, usando caché para eficiencia.
    """
    clave_carta = f"{valor}_{palo}"

    if clave_carta in IMAGENES_CARTAS_CACHE:
        return IMAGENES_CARTAS_CACHE[clave_carta]

    nombre_archivo = f"{valor} de {palo}.jpg"
    ruta_completa = CARPETA_IMAGENES_CARTAS + nombre_archivo

    imagen = pygame.image.load(ruta_completa).convert_alpha()
    imagen_escalada = pygame.transform.scale(imagen, (ancho_carta, alto_carta))
    IMAGENES_CARTAS_CACHE[clave_carta] = imagen_escalada
    return imagen_escalada


def mostrar_imagen_carta(pantalla_a_dibujar, carta_tupla, x, y):
    """
    Dibuja una carta en la pantalla, mostrando el frente o el dorso.
    """
    valor, palo, boca_arriba = carta_tupla

    if boca_arriba:
        imagen_a_mostrar = cargar_imagen_carta(valor, palo)
    else:
        imagen_a_mostrar = IMAGEN_DORSO_CARTA_CARGADA
    pantalla_a_dibujar.blit(imagen_a_mostrar, (x, y))

def generar_mazo():
    """
    Genera un mazo completo de cartas de Solitario barajado.
    Las cartas están en formato (valor, palo, boca_arriba=False).
    """
    palos = ["espada", "basto", "copa", "oro"]
    valores = [1, 2, 3, 4, 5, 6, 7, 10, 11, 12] # Valores de 1 a 7, y 10(sota), 11(caballo), 12(rey)
    mazo = []
    for palo in palos:
        for valor in valores:
            mazo.append((valor, palo, False)) # Todas las cartas inicialmente boca abajo
    random.shuffle(mazo)
    return mazo

def repartir_cartas(mazo_completo):
    """
    Reparte las cartas del mazo en las pilas del tablero y fundaciones,
    preparando el mazo de reserva y la pila de descarte.
    """
    pilas_tablero_local = [[] for _ in range(7)]
    fundaciones_local = [[] for _ in range(4)]
    mazo_reserva_temp_local = list(mazo_completo)
    pila_descarte_local = []

    # Reparto de las pilas del tablero
    for i in range(7):
        for j in range(i + 1):
            if mazo_reserva_temp_local:
                carta_base = mazo_reserva_temp_local.pop(0)
                # Solo la última carta en cada pila está boca arriba (j == i)
                pilas_tablero_local[i].append((carta_base[0], carta_base[1], j == i))

    mazo_reserva_local = mazo_reserva_temp_local # Lo que queda del mazo principal

    return pilas_tablero_local, fundaciones_local, mazo_reserva_local, pila_descarte_local

def voltear_carta_superior_pila_tablero(pila):
    """
    Voltea la carta superior de una pila del tablero si está boca abajo.
    """
    if pila and not pila[-1][2]: # Si la pila no está vacía y la última carta está boca abajo
        pila[-1] = (pila[-1][0], pila[-1][1], True) # Cambia el estado a boca arriba
        return True # Se volteó una carta
    return False # No se volteó ninguna carta o ya estaba boca arriba