# interfaz_de_usser.py
import pygame
import time
from graficos import ANCHO, ALTO, BLANCO, NEGRO, ROJO, VERDE
from cartas import (
    inicializar_recursos_graficos, cargar_imagen_carta, mostrar_imagen_carta,
    ancho_carta, alto_carta, espacio_horizontal_entre_pilas, espacio_vertical_dentro_pila,
    inicio_x_pilas, inicio_y_pilas, mazo_reserva_x, mazo_reserva_y, pila_descarte_x, pila_descarte_y,
    fundacion_final_x, fundacion_x_base, fundacion_y
)
from ranking import guardar_ranking, cargar_ranking


MENU = 0
JUGANDO = 1
RANKING = 2
PEDIR_NOMBRE_RANKING = 3


def dibujar_texto(pantalla, texto, tamaño, color, x, y):
    fuente = pygame.font.Font(None, tamaño)
    superficie_texto = fuente.render(texto, True, color)
    rect_texto = superficie_texto.get_rect(center=(x, y))
    pantalla.blit(superficie_texto, rect_texto)

def dibujar_boton_silencio(pantalla, sonido_activado_param):
    x_btn = ANCHO - 50
    y_btn = 30
    radio = 20
    color_btn = ROJO if not sonido_activado_param else BLANCO

    pygame.draw.circle(pantalla, color_btn, (x_btn, y_btn), radio, 2)

    if sonido_activado_param:
        pygame.draw.polygon(pantalla, color_btn,
                            [(x_btn - 10, y_btn - 10), (x_btn - 10, y_btn + 10), (x_btn + 5, y_btn)])
        pygame.draw.circle(pantalla, color_btn, (x_btn + 10, y_btn - 5), 5)
    else:
        pygame.draw.line(pantalla, color_btn, (x_btn - 15, y_btn - 15), (x_btn + 15, y_btn + 15), 3)
        pygame.draw.line(pantalla, color_btn, (x_btn + 15, y_btn - 15), (x_btn - 15, y_btn + 15), 3)

    return pygame.Rect(x_btn - radio, y_btn - radio, radio * 2, radio * 2)

def toggle_sonido(sonido_activado_global):
    sonido_activado_nuevo = not sonido_activado_global
    if sonido_activado_nuevo:
        pygame.mixer.music.set_volume(0.5)
        print("Sonido activado")
    else:
        pygame.mixer.music.set_volume(0.0)
        print("Sonido desactivado")
    return sonido_activado_nuevo


def dibujar_tablero(pantalla, pilas_tablero_param, mazo_reserva_param, pila_descarte_param, pilas_recoleccion_param):
    pantalla.fill(VERDE)

    for indice_pila in range(len(pilas_tablero_param)):
        pila_de_cartas = pilas_tablero_param[indice_pila]
        posicion_x_pila = inicio_x_pilas + indice_pila * (ancho_carta + espacio_horizontal_entre_pilas)

        if not pila_de_cartas:
            pygame.draw.rect(pantalla, BLANCO, (posicion_x_pila, inicio_y_pilas, ancho_carta, alto_carta), 1)

        for indice_carta in range(len(pila_de_cartas)):
            carta_completa = pila_de_cartas[indice_carta]
            posicion_y_carta = inicio_y_pilas + indice_carta * espacio_vertical_dentro_pila
            mostrar_imagen_carta(pantalla, carta_completa, posicion_x_pila, posicion_y_carta)

    if mazo_reserva_param:
        mostrar_imagen_carta(pantalla, (0, "", False), mazo_reserva_x, mazo_reserva_y)
    else:
        pygame.draw.rect(pantalla, BLANCO, (mazo_reserva_x, mazo_reserva_y, ancho_carta, alto_carta), 1)

    if pila_descarte_param:
        mostrar_imagen_carta(pantalla, pila_descarte_param[-1], pila_descarte_x, pila_descarte_y)
    else:
        pygame.draw.rect(pantalla, BLANCO, (pila_descarte_x, pila_descarte_y, ancho_carta, alto_carta), 1)
    for i in range(4):
        fundacion_x = fundacion_x_base + i * (ancho_carta + espacio_horizontal_entre_pilas)
        if pilas_recoleccion_param[i]:
            mostrar_imagen_carta(pantalla, pilas_recoleccion_param[i][-1], fundacion_x, fundacion_y)
        else:
            pygame.draw.rect(pantalla, BLANCO, (fundacion_x, fundacion_y, ancho_carta, alto_carta), 1)


def dibujar_estado_juego(pantalla_obj, pilas_tablero_param, mazo_reserva_param, pila_descarte_param, pilas_recoleccion_param, tiempo_inicio_juego_param, movimientos_realizados_param, carta_en_mano_param, posicion_carta_en_mano_param, sonido_activado_param):
    dibujar_tablero(pantalla_obj, pilas_tablero_param, mazo_reserva_param, pila_descarte_param, pilas_recoleccion_param)
    dibujar_boton_silencio(pantalla_obj, sonido_activado_param)

    tiempo_actual = int(time.time() - tiempo_inicio_juego_param)
    dibujar_texto(pantalla_obj, f"Tiempo: {tiempo_actual}s", 25, BLANCO, 100, ALTO - 30)
    dibujar_texto(pantalla_obj, f"Movimientos: {movimientos_realizados_param}", 25, BLANCO, 300, ALTO - 30)

    if carta_en_mano_param:
        for i, carta_a_dibujar in enumerate(carta_en_mano_param):
            mostrar_imagen_carta(pantalla_obj, carta_a_dibujar,
                                 posicion_carta_en_mano_param[0],
                                 posicion_carta_en_mano_param[1] + i * espacio_vertical_dentro_pila)


def manejar_menu_principal(pantalla, iniciar_juego_func, sonido_activado_param):
    pantalla.fill(VERDE)
    dibujar_texto(pantalla, "SOLITARIO", 80, BLANCO, ANCHO // 2, ALTO // 4)

    rect_jugar = pygame.Rect(ANCHO // 2 - 100, ALTO // 2 - 30, 200, 60)
    pygame.draw.rect(pantalla, ROJO, rect_jugar)
    dibujar_texto(pantalla, "JUGAR", 40, BLANCO, ANCHO // 2, ALTO // 2)

    rect_ranking = pygame.Rect(ANCHO // 2 - 100, ALTO // 2 + 50, 200, 60)
    pygame.draw.rect(pantalla, ROJO, rect_ranking)
    dibujar_texto(pantalla, "VER RANKING", 40, BLANCO, ANCHO // 2, ALTO // 2 + 80)

    rect_mute_btn = dibujar_boton_silencio(pantalla, sonido_activado_param)

    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            return False, sonido_activado_param
        if evento.type == pygame.MOUSEBUTTONDOWN:
            if rect_jugar.collidepoint(evento.pos):
                iniciar_juego_func()
                return JUGANDO, sonido_activado_param
            elif rect_ranking.collidepoint(evento.pos):
                return RANKING, sonido_activado_param
            elif rect_mute_btn.collidepoint(evento.pos):
                sonido_activado_nuevo = toggle_sonido(sonido_activado_param)
                return MENU, sonido_activado_nuevo
    return MENU, sonido_activado_param


def manejar_pantalla_ranking(pantalla, ranking_cache_param, sonido_activado_param):
    pantalla.fill(NEGRO)
    dibujar_texto(pantalla, "RANKING DE SOLITARIO", 60, BLANCO, ANCHO // 2, 50)

    y_offset = 120
    if not ranking_cache_param:
        dibujar_texto(pantalla, "No hay partidas registradas aún.", 30, BLANCO, ANCHO // 2, y_offset)
    else:
        dibujar_texto(pantalla, "Nombre", 30, BLANCO, ANCHO // 2 - 150, y_offset)
        dibujar_texto(pantalla, "Tiempo", 30, BLANCO, ANCHO // 2 + 0, y_offset)
        dibujar_texto(pantalla, "Movimientos", 30, BLANCO, ANCHO // 2 + 150, y_offset)

        y_offset += 40
        for i, entrada in enumerate(ranking_cache_param):
            if i >= 10: break
            texto_linea = (f"{entrada['Nombre']:<15}   "
                           f"{entrada['Tiempo (segundos)']:<5}s   "
                           f"{entrada['Movimientos']:<5}")

            dibujar_texto(pantalla, texto_linea, 25, BLANCO, ANCHO // 2, y_offset)
            y_offset += 30

    rect_volver_menu = pygame.Rect(ANCHO // 2 - 100, ALTO - 60, 200, 50)
    pygame.draw.rect(pantalla, ROJO, rect_volver_menu)
    dibujar_texto(pantalla, "VOLVER AL MENÚ", 30, BLANCO, ANCHO // 2, ALTO - 35)

    rect_mute_btn = dibujar_boton_silencio(pantalla, sonido_activado_param)

    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            return False, sonido_activado_param
        if evento.type == pygame.MOUSEBUTTONDOWN:
            if rect_volver_menu.collidepoint(evento.pos):
                return MENU, sonido_activado_param
            elif rect_mute_btn.collidepoint(evento.pos):
                sonido_activado_nuevo = toggle_sonido(sonido_activado_param)
                return RANKING, sonido_activado_nuevo

    return RANKING, sonido_activado_param


def manejar_pedido_nombre(pantalla, tiempo_inicio_juego_param, movimientos_realizados_param, nombre_jugador_para_ranking_global):
    nombre_actual_local = nombre_jugador_para_ranking_global
    input_activo = True

    while input_activo:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                exit()
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_RETURN:
                    input_activo = False

                    tiempo_transcurrido = int(time.time() - tiempo_inicio_juego_param)
                    guardar_ranking(nombre_actual_local, tiempo_transcurrido, movimientos_realizados_param)

                    return RANKING, nombre_actual_local

                elif evento.key == pygame.K_BACKSPACE:
                    nombre_actual_local = nombre_actual_local[:-1]
                else:
                    if len(nombre_actual_local) < 15:
                        nombre_actual_local += evento.unicode

        pantalla.fill(NEGRO)
        dibujar_texto(pantalla, "¡Felicidades! Ingresa tu nombre:", 40, BLANCO, ANCHO // 2, ALTO // 3)

        rect_input = pygame.Rect(ANCHO // 2 - 150, ALTO // 2 - 20, 300, 40)
        pygame.draw.rect(pantalla, BLANCO, rect_input, 2)
        dibujar_texto(pantalla, nombre_actual_local, 30, BLANCO, ANCHO // 2, ALTO // 2)

        dibujar_texto(pantalla, "(Presiona ENTER para guardar)", 20, BLANCO, ANCHO // 2, ALTO // 2 + 50)
        pygame.display.flip()