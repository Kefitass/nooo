# main.py
import pygame # Esta importación es necesaria para pygame.display.flip()
import time
from graficos import ANCHO, ALTO, FPS, BLANCO, NEGRO, ROJO, VERDE # Importaciones explícitas de graficos

# Importaciones explícitas desde funciones.py (ahora contiene iniciar_juego y todas las variables globales)
from funciones import (
    pilas_tablero, pilas_recoleccion, mazo_reserva, pila_descarte,
    tiempo_inicio_juego, movimientos_realizados,
    carta_en_mano, posicion_carta_en_mano, offset_x, offset_y, origen_arrastre,
    sonido_activado, nombre_jugador_para_ranking,
    MENU, JUGANDO, RANKING, PEDIR_NOMBRE_RANKING,
    obtener_color_palo, es_movimiento_valido_tablero, es_movimiento_valido_fundacion,
    manejar_eventos_generales, manejar_clics_raton_juego, manejar_arrastre_raton,
    manejar_soltar_raton, manejar_clic_mazo_reserva, manejar_clic_pila_descarte,
    manejar_clic_pilas_tablero, manejar_soltar_en_tablero, manejar_soltar_en_fundacion,
    devolver_carta_a_origen, manejar_estado_jugando,
    iniciar_juego # AHORA iniciar_juego está de vuelta en funciones.py y se importa desde aquí
)

# Importaciones explícitas desde ranking.py
from ranking import cargar_ranking, guardar_ranking

# Importaciones explícitas desde pygame_init.py
from pygame_init import initialize_pygame_environment, control_game_loop_timing, quit_pygame_environment

# Importaciones explícitas desde interfaz_de_usser.py
from interfaz_de_usser import (
    dibujar_texto, dibujar_boton_silencio, toggle_sonido,
    dibujar_tablero, dibujar_estado_juego,
    manejar_menu_principal, manejar_pantalla_ranking, manejar_pedido_nombre
)

# Importaciones explícitas de cartas.py
from cartas import inicializar_recursos_graficos


# LLAMA A LA FUNCIÓN DE INICIALIZACIÓN DEL NUEVO MÓDULO (desde pygame_init)
pantalla, reloj = initialize_pygame_environment()

# inicializar_recursos_graficos ahora se llama directamente, ya que se importa desde cartas.py
inicializar_recursos_graficos()


# Las constantes de estado (MENU, JUGANDO, etc.) se importan directamente de funciones.py
estado_juego = MENU # Se inicializa el estado del juego
estado_anterior = None #esto vendria a ser para detectar cambios de estado y cargar el ranking una vez

ranking_cache = [] # Esta variable global se mantiene en main.py para la gestión de la interfaz de ranking.


ejecutando = True
while ejecutando:
    # LLAMA A LA FUNCIÓN PARA CONTROLAR LOS FPS (desde pygame_init)
    control_game_loop_timing(reloj)

    if estado_juego == RANKING and estado_anterior != RANKING:
        ranking_cache = cargar_ranking()
    estado_anterior = estado_juego

    if estado_juego == MENU:
        nuevo_estado, sonido_activado = manejar_menu_principal(
            pantalla,
            iniciar_juego, # iniciar_juego se importa directamente de funciones.py
            sonido_activado # sonido_activado se importa de funciones.py
        )
    elif estado_juego == JUGANDO:
        dibujar_estado_juego(
            pantalla, pilas_tablero, mazo_reserva, pila_descarte, pilas_recoleccion,
            tiempo_inicio_juego, movimientos_realizados, carta_en_mano, posicion_carta_en_mano,
            sonido_activado
        )
        nuevo_estado = manejar_estado_jugando(pantalla, estado_juego)

    elif estado_juego == RANKING:
        nuevo_estado, sonido_activado = manejar_pantalla_ranking(pantalla, ranking_cache, sonido_activado)
    elif estado_juego == PEDIR_NOMBRE_RANKING:
        nuevo_estado, nombre_jugador_para_ranking = manejar_pedido_nombre(
            pantalla, tiempo_inicio_juego, movimientos_realizados, nombre_jugador_para_ranking
        )

    if nuevo_estado is False:
        ejecutando = False
    else:
        estado_juego = nuevo_estado

    pygame.display.flip()

# LLAMA A LA FUNCIÓN PARA FINALIZAR PYGAME (desde pygame_init)
quit_pygame_environment()