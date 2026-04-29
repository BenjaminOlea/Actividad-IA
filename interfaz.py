import pygame
import sys
from tablero import tablero
from jugador import jugador

# --- 1. CONFIGURACIÓN GENERAL Y COLORES ---
pygame.init()
ANCHO, ALTO = 480, 800
TAMANO_CASILLA = ANCHO // 8
OFFSET_Y = (ALTO - ANCHO) // 2

COLOR_FONDO = (25, 25, 25)
COLOR_MADERA_CLARA = (239, 217, 181)
COLOR_MADERA_OSCURA = (181, 136, 99)
BLANCO = (245, 245, 245)
NEGRO = (40, 40, 40)
ORO = (255, 215, 0)
SOMBRA = (15, 15, 15)

VERDE_ACCION = (46, 125, 50)
ROJO_ALERTA = (183, 28, 28)
AZUL_MENU = (13, 71, 161)

pantalla = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("Damas vs Bots!")

# Fuentes para textos y botones
fuente_titulo = pygame.font.SysFont("Verdana", 50, bold=True)
fuente_pnt = pygame.font.SysFont("Trebuchet MS", 30, bold=True)
fuente_btn = pygame.font.SysFont("Trebuchet MS", 20, bold=True)

# --- 2. LÓGICA DE APOYO Y ANIMACIÓN ---

def dibujar_tablero_sin_pieza_movil(pantalla, matriz, pos_origen, pos_destino):
    """ Dibuja el estado actual del tablero pero oculta la pieza que se está moviendo """
    pantalla.fill(COLOR_FONDO)
    for f in range(8):
        for c in range(8):
            rect = pygame.Rect(c*TAMANO_CASILLA, OFFSET_Y + f*TAMANO_CASILLA, TAMANO_CASILLA, TAMANO_CASILLA)
            color = COLOR_MADERA_CLARA if (f+c)%2 == 0 else COLOR_MADERA_OSCURA
            pygame.draw.rect(pantalla, color, rect)
            
            # Saltamos la casilla de origen y destino para no dibujar la pieza estática ahí
            if (f, c) == pos_origen or (f, c) == pos_destino: 
                continue 
            
            try: 
                p = matriz[f][c]
            except: 
                p = " "
                
            if p != " ":
                color_p = BLANCO if p.lower() == 'b' else NEGRO
                pygame.draw.circle(pantalla, color_p, rect.center, TAMANO_CASILLA//2 - 10)
                if p.isupper(): # Si es Dama, le dibujamos un centro dorado
                    pygame.draw.circle(pantalla, ORO, rect.center, 10)

def animar_movimiento(pantalla, reloj, matriz, inicio, fin, pieza_char, fps=60):
    """ Interpola linealmente la posición de una pieza entre su inicio y fin para crear una animación """
    x_ini, y_ini = inicio[1] * TAMANO_CASILLA, OFFSET_Y + (inicio[0] * TAMANO_CASILLA)
    x_fin, y_fin = fin[1] * TAMANO_CASILLA, OFFSET_Y + (fin[0] * TAMANO_CASILLA)
    frames = 12
    
    for i in range(frames):
        x = x_ini + (x_fin - x_ini) * i / frames
        y = y_ini + (y_fin - y_ini) * i / frames
        
        dibujar_tablero_sin_pieza_movil(pantalla, matriz, inicio, fin)
        
        color_p = BLANCO if pieza_char.lower() == 'b' else NEGRO
        pygame.draw.circle(pantalla, color_p, (int(x + TAMANO_CASILLA//2), int(y + TAMANO_CASILLA//2)), TAMANO_CASILLA//2 - 10)
        if pieza_char.isupper(): 
            pygame.draw.circle(pantalla, ORO, (int(x + TAMANO_CASILLA//2), int(y + TAMANO_CASILLA//2)), 10)
            
        pygame.display.update()
        reloj.tick(fps)

def encontrar_movimiento_bot(matriz_vieja, matriz_nueva, turno):
    """ Compara el tablero antes y después del turno de la IA para saber de dónde a dónde saltó """
    origen = destino = None
    for f in range(8):
        for c in range(8):
            v, n = matriz_vieja[f][c], matriz_nueva[f][c]
            if v.lower() == turno and n == " ": 
                origen = (f, c)
            elif (v == " " or v.lower() != turno) and n.lower() == turno: 
                destino = (f, c)
    return origen, destino

def obtener_movimientos_validos(matriz, fila, col, simbolo):
    """ Consulta a la clase de búsqueda cuáles son los movimientos legales para una pieza específica """
    from busqueda import busqueda
    from estado import estado
    
    b = busqueda(matriz, simbolo, 'n' if simbolo == 'b' else 'b')
    e_actual = estado(matriz, None, "", 0)
    sucesores = b.obtener_sucesores(e_actual, simbolo)
    
    validos = []
    for s in sucesores:
        accion = s.get_accion()
        if f"{fila},{col}" in accion:
            try:
                f_dest, c_dest = map(int, accion.split(" a ")[1].split(","))
                validos.append((f_dest, c_dest, s.get_estado()))
            except: 
                pass
    return validos

# --- 3. ELEMENTOS VISUALES DE LA INTERFAZ ---

def dibujar_boton_menu(texto, y_pos, color_base):
    rect_sombra = pygame.Rect(ANCHO//2 - 128, y_pos + 4, 260, 55)
    pygame.draw.rect(pantalla, SOMBRA, rect_sombra, border_radius=15)
    
    rect = pygame.Rect(ANCHO//2 - 130, y_pos, 260, 55)
    pygame.draw.rect(pantalla, color_base, rect, border_radius=15)
    pygame.draw.rect(pantalla, BLANCO, rect, 2, border_radius=15) # Borde blanco
    
    txt = fuente_btn.render(texto, True, BLANCO)
    pantalla.blit(txt, (rect.centerx - txt.get_width()//2, rect.centery - txt.get_height()//2))
    return rect

def dibujar_boton_pequeno(y_pos, texto, color=ROJO_ALERTA):
    rect = pygame.Rect(ANCHO - 150, y_pos, 140, 40)
    pygame.draw.rect(pantalla, SOMBRA, (rect.x+2, rect.y+2, 140, 40), border_radius=8)
    pygame.draw.rect(pantalla, color, rect, border_radius=8)
    txt = fuente_btn.render(texto, True, BLANCO)
    pantalla.blit(txt, (rect.centerx - txt.get_width()//2, rect.centery - txt.get_height()//2))
    return rect

def pantalla_victoria(mensaje):
    """ Muestra un cartel superpuesto oscuro con el ganador """
    sup = pygame.Surface((ANCHO, ALTO))
    sup.set_alpha(220)
    sup.fill((0, 0, 0))
    pantalla.blit(sup, (0, 0))
    
    txt = fuente_pnt.render(mensaje, True, ORO)
    pantalla.blit(txt, (ANCHO//2 - txt.get_width()//2, ALTO//2 - 20))
    pygame.display.flip()
    pygame.time.wait(2000)

def mostrar_menu():
    """ Ciclo de la pantalla de inicio, retorna el modo de juego elegido """
    while True:
        pantalla.fill(COLOR_FONDO)
        
        txt_tit = fuente_titulo.render("DAMAS", True, ORO)
        txt_vs = fuente_pnt.render("VS", True, BLANCO)
        txt_bots = fuente_pnt.render("BOTS!", True, ROJO_ALERTA)
        pantalla.blit(txt_tit, (ANCHO//2 - txt_tit.get_width()//2, 120))
        pantalla.blit(txt_vs, (ANCHO//2 - txt_tit.get_width()//2, 185))
        pantalla.blit(txt_bots, (ANCHO//2 - txt_bots.get_width()//2, 185))
        
        btn1 = dibujar_boton_menu("HUMANO VS HUMANO", 320, (60, 60, 60))
        btn2 = dibujar_boton_menu("HUMANO VS BOT", 400, VERDE_ACCION)
        btn3 = dibujar_boton_menu("BOT VS BOT", 480, AZUL_MENU)
        
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT: 
                pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if btn1.collidepoint(event.pos): return 1
                if btn2.collidepoint(event.pos): return 2
                if btn3.collidepoint(event.pos): return 3

# --- 4. CICLO PRINCIPAL DE JUEGO ---

def jugar(modo):
    # Configuración de los jugadores según el modo seleccionado
    if modo == 1: 
        j1, j2 = jugador("Blanco", False), jugador("Negro", False)
    elif modo == 2: 
        j1, j2 = jugador("Humano", False), jugador("IA", True)
    else: 
        j1, j2 = jugador("IA 1", True), jugador("IA 2", True)
        
    tab, turno, seleccionada, movs_posibles = tablero(j1, j2), 'b', None, []
    reloj = pygame.time.Clock()

    while True:
        pantalla.fill(COLOR_FONDO)
        
        txt_t = fuente_btn.render(f"TURNO: {'BLANCAS' if turno == 'b' else 'NEGRAS'}", True, ORO)
        pantalla.blit(txt_t, (20, 25))
        
        btn_r_n = btn_r_b = btn_salir = None
        if modo != 3:
            btn_r_n = dibujar_boton_pequeno(20, "RENDIRSE", ROJO_ALERTA)
            btn_r_b = dibujar_boton_pequeno(ALTO - 60, "RENDIRSE", ROJO_ALERTA)
        else:
            btn_salir = dibujar_boton_pequeno(ALTO - 60, "SALIR AL MENÚ", AZUL_MENU)
        
        for f in range(8):
            for c in range(8):
                rect = pygame.Rect(c*TAMANO_CASILLA, OFFSET_Y + f*TAMANO_CASILLA, TAMANO_CASILLA, TAMANO_CASILLA)
                col = COLOR_MADERA_CLARA if (f+c)%2 == 0 else COLOR_MADERA_OSCURA
                pygame.draw.rect(pantalla, col, rect)
                
                try: 
                    p = tab.matriz[f][c]
                except: 
                    p = " "
                    
                if p != " ":
                    cp = BLANCO if p.lower() == 'b' else NEGRO
                    pygame.draw.circle(pantalla, cp, rect.center, TAMANO_CASILLA//2 - 10)
                    if p.isupper(): 
                        pygame.draw.circle(pantalla, ORO, rect.center, 10)
                
                if seleccionada == (f, c): 
                    pygame.draw.rect(pantalla, VERDE_ACCION, rect, 4)
                
                for mf, mc, _ in movs_posibles:
                    if f == mf and c == mc: 
                        pygame.draw.circle(pantalla, VERDE_ACCION, rect.center, 8)

        pygame.display.flip()

        # Condición de Victoria 
        b_vivas = sum(fila.count('b') + fila.count('B') for fila in tab.matriz)
        n_vivas = sum(fila.count('n') + fila.count('N') for fila in tab.matriz)
        if b_vivas == 0: pantalla_victoria("¡GANAN NEGRAS!"); return 
        if n_vivas == 0: pantalla_victoria("¡GANAN BLANCAS!"); return 

        # Captura de Eventos Globales de Botones
        eventos = pygame.event.get()
        for ev in eventos:
            if ev.type == pygame.QUIT: 
                pygame.quit(); sys.exit()
            if ev.type == pygame.MOUSEBUTTONDOWN:
                if btn_r_n and btn_r_n.collidepoint(ev.pos): pantalla_victoria("GANAN BLANCAS"); return
                if btn_r_b and btn_r_b.collidepoint(ev.pos): pantalla_victoria("GANAN NEGRAS"); return
                if btn_salir and btn_salir.collidepoint(ev.pos): return

        # Lógica de Turnos
        j_actual = j1 if turno == 'b' else j2
        
        if j_actual.es_bot:
            m_vieja = [f[:] for f in tab.matriz] # Copia del tablero actual
            
            # Espera 400ms para que se vea el turno, pero sigue escuchando el botón de Salir
            t_ini = pygame.time.get_ticks()
            while pygame.time.get_ticks() - t_ini < 400:
                for ev in pygame.event.get():
                    if ev.type == pygame.MOUSEBUTTONDOWN and btn_salir and btn_salir.collidepoint(ev.pos): 
                        return
            
            # Ejecuta Minimax
            n_matriz = j_actual.toma_turno_automatico(tab.matriz, turno)
            if n_matriz is None: 
                pantalla_victoria("BLOQUEO - FIN"); return
            
            ori, dest = encontrar_movimiento_bot(m_vieja, n_matriz, turno)
            if ori and dest: 
                animar_movimiento(pantalla, reloj, m_vieja, ori, dest, m_vieja[ori[0]][ori[1]])
            
            tab.matriz, turno = n_matriz, ('n' if turno == 'b' else 'b')
            continue
            
        else:
            # Lógica de input para Humanos
            for ev in eventos:
                if ev.type == pygame.MOUSEBUTTONDOWN:
                    x, y = ev.pos
                    if OFFSET_Y <= y <= OFFSET_Y + ANCHO:
                        c, f = x // TAMANO_CASILLA, (y - OFFSET_Y) // TAMANO_CASILLA
                        
                        if tab.matriz[f][c].lower() == turno:
                            seleccionada, movs_posibles = (f, c), obtener_movimientos_validos(tab.matriz, f, c, turno)
                        else:
                            for mf, mc, nm in movs_posibles:
                                if f == mf and c == mc:
                                    animar_movimiento(pantalla, reloj, tab.matriz, seleccionada, (f, c), tab.matriz[seleccionada[0]][seleccionada[1]])
                                    tab.matriz, turno, seleccionada, movs_posibles = nm, ('n' if turno == 'b' else 'b'), None, []
                                    break
                            else: 
                                seleccionada = None; movs_posibles = []
        reloj.tick(30)

if __name__ == "__main__":
    while True:
        m = mostrar_menu()
        jugar(m)