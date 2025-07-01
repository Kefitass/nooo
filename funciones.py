from graficos import *
import pygame
import random
import csv # DEJA ESTA LÍNEA SI LA TENÍAS ORIGINALMENTE Y NO ESTABA COMENTADA
import time
import os # DEJA ESTA LÍNEA SI LA TENÍAS ORIGINALMENTE Y NO ESTABA COMENTADA

# Importaciones para que funciones.py tenga todo lo que necesita para su lógica
from ranking import guardar_ranking, cargar_ranking # Necesario para manejar_pedido_nombre
from cartas import generar_mazo, repartir_cartas, voltear_carta_superior_pila_tablero # Necesario para iniciar_juego y lógica de juego
from cartas import ancho_carta, alto_carta, espacio_horizontal_entre_pilas, espacio_vertical_dentro_pila, inicio_x_pilas, inicio_y_pilas, mazo_reserva_x, mazo_reserva_y, pila_descarte_x, pila_descarte_y, fundacion_final_x, fundacion_x_base, fundacion_y, mostrar_imagen_carta # Necesario para dibujar_tablero, etc.
from interfaz_de_usser import dibujar_texto, dibujar_boton_silencio, toggle_sonido, dibujar_tablero, dibujar_estado_juego # Necesario para llamadas de UI

# ELIMINADO: from pygame_init import iniciar_juego <-- ¡Esto causaba la importación circular!


# --- Variables Globales del ESTADO DEL JUEGO (gestionadas principalmente en este módulo) ---
pilas_tablero = []
pilas_recoleccion = []
mazo_reserva = []
pila_descarte = []

tiempo_inicio_juego = 0
movimientos_realizados = 0

carta_en_mano = None
posicion_carta_en_mano = (0, 0)
offset_x = 0
offset_y = 0
origen_arrastre = None

sonido_activado = True # Se mantiene aquí, ya que manejar_clics_raton_juego lo modifica.

nombre_jugador_para_ranking = "" # Se mantiene aquí, ya que manejar_pedido_nombre lo usa.

# --- Constantes de Estado de Juego ---
MENU = 0
JUGANDO = 1
RANKING = 2
PEDIR_NOMBRE_RANKING = 3


# --- Funciones de Lógica del Juego (Reubicadas para romper circularidad) ---

def iniciar_juego():
    """
    Inicializa el estado del juego (pilas, mazos, contadores) para una nueva partida.
    Esta función regresa a 'funciones.py'.
    """
    global pilas_tablero, pilas_recoleccion, mazo_reserva, pila_descarte
    global tiempo_inicio_juego, movimientos_realizados
    global carta_en_mano, posicion_carta_en_mano, offset_x, offset_y, origen_arrastre

    mazo_completo_barajado = generar_mazo() # Usa generar_mazo de cartas.py

    pilas_tablero_nuevas, fundaciones_nuevas, mazo_reserva_nuevo, pila_descarte_nueva = repartir_cartas(mazo_completo_barajado) # Usa repartir_cartas de cartas.py
    pilas_tablero = pilas_tablero_nuevas
    pilas_recoleccion = fundaciones_nuevas
    mazo_reserva = mazo_reserva_nuevo
    pila_descarte = pila_descarte_nueva

    tiempo_inicio_juego = time.time()
    movimientos_realizados = 0

    carta_en_mano = None
    origen_arrastre = None


def obtener_color_palo(palo):
    if palo in ["oro", "copa"]:
        return "rojo"
    elif palo in ["espada", "basto"]:
        return "negro"
    return None

def es_movimiento_valido_tablero(carta_a_mover, pila_destino):
    valor_mover = carta_a_mover[0]
    palo_mover = carta_a_mover[1]
    color_mover = obtener_color_palo(palo_mover)

    if not pila_destino:
        return valor_mover == 12
    else:
        carta_superior_destino = pila_destino[-1]
        valor_destino = carta_superior_destino[0]
        palo_destino = carta_superior_destino[1]
        color_destino = obtener_color_palo(palo_destino)

        condicion_valor = valor_mover == valor_destino - 1
        condicion_color = color_mover != color_destino

        return condicion_valor and condicion_color

def es_movimiento_valido_fundacion(carta_a_mover, pila_destino):
    valor_mover = carta_a_mover[0]
    palo_mover = carta_a_mover[1]
    if not pila_destino:
        return valor_mover == 1
    else:
        carta_superior_destino = pila_destino[-1]
        valor_destino = carta_superior_destino[0]
        palo_destino = carta_superior_destino[1]

        condicion_valor = valor_mover == valor_destino + 1
        condicion_palo = palo_mover == palo_destino

        return condicion_valor and condicion_palo


def manejar_eventos_generales(evento, estado_juego_param):
    if evento.type == pygame.QUIT:
        return False, "SALIR"

    if evento.type == pygame.KEYDOWN and evento.key == pygame.K_g:
        return True, PEDIR_NOMBRE_RANKING

    return True, estado_juego_param

def manejar_clics_raton_juego(evento_pos, mouse_x, mouse_y, pantalla_obj, sonido_activado_var):
    global movimientos_realizados, carta_en_mano, posicion_carta_en_mano, offset_x, offset_y, origen_arrastre
    global pilas_tablero, pilas_recoleccion, mazo_reserva, pila_descarte
    global sonido_activado # Para modificar el global

    # dibujar_boton_silencio y toggle_sonido ahora son importados de interfaz_de_usser.py
    if dibujar_boton_silencio(pantalla_obj, sonido_activado_var).collidepoint(evento_pos):
        sonido_activado = toggle_sonido(sonido_activado_var) # toggle_sonido ahora devuelve el nuevo estado
        return True
    if manejar_clic_mazo_reserva(mouse_x, mouse_y):
        return
    if manejar_clic_pila_descarte(mouse_x, mouse_y):
        return
    if manejar_clic_pilas_tablero(mouse_x, mouse_y):
        return

def manejar_arrastre_raton(evento):
    global posicion_carta_en_mano, offset_x, offset_y, carta_en_mano
    if carta_en_mano:
        mouse_x, mouse_y = evento.pos
        posicion_carta_en_mano = (mouse_x - offset_x, mouse_y - offset_y)

def manejar_soltar_raton(evento):
    global movimientos_realizados, carta_en_mano, origen_arrastre
    global pilas_tablero, pilas_recoleccion, pila_descarte

    if not carta_en_mano:
        return

    mouse_x, mouse_y = evento.pos
    soltada_correctamente = False
    carta_top_mover = carta_en_mano[0]

    soltada_en_tablero = manejar_soltar_en_tablero(mouse_x, mouse_y, carta_top_mover)
    if soltada_en_tablero:
        soltada_correctamente = True

    if not soltada_correctamente:
        soltada_en_fundacion = manejar_soltar_en_fundacion(mouse_x, mouse_y, carta_top_mover)
        if soltada_en_fundacion:
            soltada_correctamente = True

    if not soltada_correctamente:
        devolver_carta_a_origen()

    if soltada_correctamente and origen_arrastre and origen_arrastre[0] == "tablero":
        voltear_carta_superior_pila_tablero(pilas_tablero[origen_arrastre[1]])

    carta_en_mano = None
    origen_arrastre = None


def manejar_clic_mazo_reserva(mouse_x, mouse_y):
    global movimientos_realizados, mazo_reserva, pila_descarte
    if mazo_reserva:
        rect_mazo_reserva = pygame.Rect(mazo_reserva_x, mazo_reserva_y, ancho_carta, alto_carta)
        if rect_mazo_reserva.collidepoint(mouse_x, mouse_y):
            if mazo_reserva:
                carta_descarte = mazo_reserva.pop()
                pila_descarte.append((carta_descarte[0], carta_descarte[1], True))
                movimientos_realizados += 1
                return True
    return False


def manejar_clic_pila_descarte(mouse_x, mouse_y):
    global carta_en_mano, origen_arrastre, offset_x, offset_y, pila_descarte
    if pila_descarte:
        rect_pila_descarte = pygame.Rect(pila_descarte_x, pila_descarte_y, ancho_carta, alto_carta)
        if rect_pila_descarte.collidepoint(mouse_x, mouse_y):
            carta_selec = pila_descarte[-1]
            if carta_selec[2]:
                carta_en_mano = [pila_descarte.pop()]
                origen_arrastre = ("descarte", -1, -1)
                offset_x = mouse_x - pila_descarte_x
                offset_y = mouse_y - pila_descarte_y
                return True
    return False


def manejar_clic_pilas_tablero(mouse_x, mouse_y):
    global carta_en_mano, origen_arrastre, offset_x, offset_y, pilas_tablero
    for indice_pila, pila_de_cartas in enumerate(pilas_tablero):
        posicion_x_pila = inicio_x_pilas + indice_pila * (ancho_carta + espacio_horizontal_entre_pilas)

        for indice_carta in range(len(pila_de_cartas) - 1, -1, -1):
            carta_actual = pila_de_cartas[indice_carta]
            posicion_y_carta = inicio_y_pilas + indice_carta * espacio_vertical_dentro_pila

            altura_rect = espacio_vertical_dentro_pila if indice_carta < len(pila_de_cartas) - 1 else alto_carta
            rect_carta = pygame.Rect(posicion_x_pila, posicion_y_carta, ancho_carta, altura_rect)

            if rect_carta.collidepoint(mouse_x, mouse_y) and carta_actual[2]:
                carta_en_mano = pila_de_cartas[indice_carta:]
                pilas_tablero[indice_pila] = pilas_tablero[indice_pila][:indice_carta]

                origen_arrastre = ("tablero", indice_pila, indice_carta)
                offset_x = mouse_x - posicion_x_pila
                offset_y = mouse_y - posicion_y_carta
                return True
    return False


def manejar_soltar_en_tablero(mouse_x, mouse_y, carta_top_mover):
    global movimientos_realizados, carta_en_mano, origen_arrastre, pilas_tablero
    soltada_correctamente = False

    for target_pila_idx, pila_destino in enumerate(pilas_tablero):
        target_x_pila = inicio_x_pilas + target_pila_idx * (ancho_carta + espacio_horizontal_entre_pilas)

        if pila_destino:
            ultima_carta_y = inicio_y_pilas + (len(pila_destino) - 1) * espacio_vertical_dentro_pila
            rect_destino = pygame.Rect(target_x_pila, ultima_carta_y, ancho_carta, alto_carta)
        else:
            rect_destino = pygame.Rect(target_x_pila, inicio_y_pilas, ancho_carta, alto_carta)

        if rect_destino.collidepoint(mouse_x, mouse_y):
            if origen_arrastre[0] == "tablero" and origen_arrastre[1] == target_pila_idx:
                for c in reversed(carta_en_mano):
                    pilas_tablero[origen_arrastre[1]].insert(origen_arrastre[2], c)
                soltada_correctamente = True
            else:
                if es_movimiento_valido_tablero(carta_top_mover, pila_destino):
                    pilas_tablero[target_pila_idx].extend(carta_en_mano)
                    soltada_correctamente = True
                    movimientos_realizados += 1
                else:
                    print("Movimiento inválido en tablero")
            return soltada_correctamente

    return False


def manejar_soltar_en_fundacion(mouse_x, mouse_y, carta_top_mover):
    global movimientos_realizados, carta_en_mano, origen_arrastre, pilas_recoleccion
    soltada_correctamente = False

    for i in range(4):
        fundacion_x = fundacion_x_base + i * (ancho_carta + espacio_horizontal_entre_pilas)
        rect_fundacion = pygame.Rect(fundacion_x, fundacion_y, ancho_carta, alto_carta)

        if rect_fundacion.collidepoint(mouse_x, mouse_y):
            if len(carta_en_mano) == 1:
                carta_unica_mover = carta_en_mano[0]
                if origen_arrastre[0] == "fundacion" and origen_arrastre[1] == i:
                    pilas_recoleccion[i].extend(carta_en_mano)
                    soltada_correctamente = True
                else:
                    if es_movimiento_valido_fundacion(carta_unica_mover, pilas_recoleccion[i]):
                        pilas_recoleccion[i].extend(carta_en_mano)
                        soltada_correctamente = True
                        movimientos_realizados += 1
                    else:
                        print("Movimiento inválido en fundación")
            else:
                print("Movimiento inválido, solo se puede mover una carta.")
            return soltada_correctamente
    return False


def devolver_carta_a_origen():
    global carta_en_mano, origen_arrastre, pilas_tablero, pila_descarte, pilas_recoleccion
    if origen_arrastre[0] == "tablero":
        for c in reversed(carta_en_mano):
            pilas_tablero[origen_arrastre[1]].insert(origen_arrastre[2], c)
    elif origen_arrastre[0] == "descarte":
        pila_descarte.extend(carta_en_mano)
    elif origen_arrastre[0] == "fundacion":
        pilas_recoleccion[origen_arrastre[1]].extend(carta_en_mano)
    print("Movimiento inválido o no reconocido, la carta vuelve a su origen.")


def manejar_estado_jugando(pantalla, estado_juego_param):
    global carta_en_mano, posicion_carta_en_mano, offset_x, offset_y, origen_arrastre
    global sonido_activado # Accedemos a sonido_activado globalmente aquí

    for evento in pygame.event.get():
        continuar_loop_eventos, nuevo_estado = manejar_eventos_generales(evento, estado_juego_param)
        if not continuar_loop_eventos:
            return False
        if nuevo_estado != estado_juego_param:
            return nuevo_estado

        if evento.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = evento.pos
            manejar_clics_raton_juego(evento.pos, mouse_x, mouse_y, pantalla, sonido_activado)

        elif evento.type == pygame.MOUSEMOTION:
            manejar_arrastre_raton(evento)

        elif evento.type == pygame.MOUSEBUTTONUP:
            if carta_en_mano:
                mouse_x, mouse_y = evento.pos
                soltada_correctamente = False
                carta_top_mover = carta_en_mano[0]

                soltada_en_tablero = manejar_soltar_en_tablero(mouse_x, mouse_y, carta_top_mover)
                if soltada_en_tablero:
                    soltada_correctamente = True

                if not soltada_correctamente:
                    soltada_en_fundacion = manejar_soltar_en_fundacion(mouse_x, mouse_y, carta_top_mover)
                    if soltada_en_fundacion:
                        soltada_correctamente = True

                if not soltada_correctamente:
                    devolver_carta_a_origen()

                if soltada_correctamente and origen_arrastre and origen_arrastre[0] == "tablero":
                    voltear_carta_superior_pila_tablero(pilas_tablero[origen_arrastre[1]])

                carta_en_mano = None
                origen_arrastre = None

    dibujar_estado_juego(
        pantalla, pilas_tablero, mazo_reserva, pila_descarte, pilas_recoleccion,
        tiempo_inicio_juego, movimientos_realizados, carta_en_mano, posicion_carta_en_mano,
        sonido_activado # Se pasa sonido_activado para el dibujo
    )

    return estado_juego_param

# Este es tu comentario original.
##############me falta el boton para volver las cartas y creo que nada mas, quizas dropear las cartas en el lugar ese de arriba