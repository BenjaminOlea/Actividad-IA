from estado import estado
import math
import random

class busqueda:
    def __init__(self, EI, s_max, s_min):
        self.estado_inicial = estado(EI, None, "Origen", 0)
        self.estado_solucion = None
        self.s_max = s_max
        self.s_min = s_min
        self.estados_descubiertos = 0

    
    from estado import estado

    def calcular_heuristica(self, e):
        m = e.get_estado()
        score_max = 0
        score_min = 0
        
        for f in range(8):
            for c in range(8):
                pieza = m[f][c]
                if pieza == " ": continue
                
                # 1. Valor base de las piezas (10 por peón, 30 por Dama)
                valor = 10 if pieza.islower() else 30
                
                # 2. Incentivo por avanzar (rompe el bucle de quedarse quieto)
                # Las blancas avanzan hacia la fila 0, las negras hacia la fila 7
                if pieza == 'b':
                    valor += (7 - f)  # Gana hasta 7 puntos extra por acercarse a coronar
                elif pieza == 'n':
                    valor += f        # Gana hasta 7 puntos extra por acercarse a coronar
                
                # Sumar al jugador correspondiente
                if pieza.lower() == self.s_max.lower():
                    score_max += valor
                elif pieza.lower() == self.s_min.lower():
                    score_min += valor
                    
        # 3. Pequeño factor aleatorio (0 a 0.5) para romper empates en posiciones idénticas
        azar = random.uniform(0, 0.5)
        
        return (score_max - score_min) + azar

    def _buscar_saltos(self, tablero_actual, f, c, pieza, e_padre, f_original=None, c_original=None):
        # Recordamos el origen exacto desde el primer salto
        if f_original is None:
            f_original = f
            c_original = c
            
        saltos_encontrados = []
        simbolo_jugador = pieza.lower()
        simbolo_dama = simbolo_jugador.upper()
        
        if simbolo_jugador == 'b': direcciones = [(-1, -1), (-1, 1)]
        else: direcciones = [(1, -1), (1, 1)]
        dir_dama = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
        
        dirs_actuales = dir_dama if pieza == simbolo_dama else direcciones
        
        for df, dc in dirs_actuales:
            nf, nc = f + df, c + dc
            nf_salto, nc_salto = f + 2*df, c + 2*dc
            
            if 0 <= nf_salto < 8 and 0 <= nc_salto < 8:
                pieza_media = tablero_actual[nf][nc].lower()
                if pieza_media != " " and pieza_media != simbolo_jugador and tablero_actual[nf_salto][nc_salto] == " ":
                    nuevo_tablero = [fila[:] for fila in tablero_actual]
                    nuevo_tablero[nf_salto][nc_salto] = pieza
                    nuevo_tablero[nf][nc] = " " 
                    nuevo_tablero[f][c] = " "   
                    
                    coronada = False
                    if (simbolo_jugador == 'b' and nf_salto == 0) or (simbolo_jugador == 'n' and nf_salto == 7):
                        nuevo_tablero[nf_salto][nc_salto] = simbolo_dama
                        coronada = True
                    
                    mas_saltos = []
                    if not coronada:
                        # Pasamos f_original y c_original en la recursividad
                        mas_saltos = self._buscar_saltos(nuevo_tablero, nf_salto, nc_salto, pieza, e_padre, f_original, c_original)
                    
                    if mas_saltos:
                        saltos_encontrados.extend(mas_saltos)
                    else:
                        from estado import estado
                        saltos_encontrados.append(estado(nuevo_tablero, e_padre, f"Captura {f_original},{c_original} a {nf_salto},{nc_salto}", e_padre.nivel + 1))
                        
        return saltos_encontrados

    def obtener_sucesores(self, e, simbolo_jugador):
        m = e.get_estado()
        sucesores_movimientos = []
        sucesores_saltos = [] # Separar para obligar a comer si es posible
        simbolo_dama = simbolo_jugador.upper()
        
        if simbolo_jugador == 'b': direcciones = [(-1, -1), (-1, 1)]
        else: direcciones = [(1, -1), (1, 1)]
        dir_dama = [(-1, -1), (-1, 1), (1, -1), (1, 1)]

        for f in range(8):
            for c in range(8):
                pieza = m[f][c]
                if pieza.lower() != simbolo_jugador: continue
                
                # 1. Buscar saltos (capturas)
                saltos = self._buscar_saltos(m, f, c, pieza, e)
                sucesores_saltos.extend(saltos)
                
                # 2. Buscar movimientos simples (solo si no hay saltos obligatorios)
                dirs_actuales = dir_dama if pieza == simbolo_dama else direcciones
                for df, dc in dirs_actuales:
                    nf, nc = f + df, c + dc
                    if 0 <= nf < 8 and 0 <= nc < 8 and m[nf][nc] == " ":
                        nuevo_tablero = [fila[:] for fila in m]
                        nuevo_tablero[nf][nc] = pieza
                        nuevo_tablero[f][c] = " "
                        if (simbolo_jugador == 'b' and nf == 0) or (simbolo_jugador == 'n' and nf == 7):
                            nuevo_tablero[nf][nc] = simbolo_dama
                        from estado import estado
                        sucesores_movimientos.append(estado(nuevo_tablero, e, f"Mover {f},{c} a {nf},{nc}", e.nivel + 1))

        # En las damas, si puedes comer, es obligatorio
        if sucesores_saltos:
            return sucesores_saltos
        return sucesores_movimientos

    def juego_terminado(self, e):
        m = e.get_estado()
        b = sum(fila.count('b') + fila.count('B') for fila in m)
        n = sum(fila.count('n') + fila.count('N') for fila in m)
        return b == 0 or n == 0

    def algoritmo_minimax_alpha_beta(self, e, profundidad, alpha, beta, turno_max):
        # Implementación Minimax con Poda Alfa-Beta
        if profundidad == 0 or self.juego_terminado(e):
            e.set_heuristica(self.calcular_heuristica(e))
            self.estados_descubiertos += 1
            return e.get_heuristica()

        if turno_max:
            maximo = -math.inf
            hijos = self.obtener_sucesores(e, self.s_max)
            
            if not hijos: return self.calcular_heuristica(e)
            
            e_max = [filas[:] for filas in hijos[0].get_estado()]

            for hijo in hijos:
                eval = self.algoritmo_minimax_alpha_beta(hijo, profundidad - 1, alpha, beta, False)
                if eval > maximo:
                    maximo = eval
                    e_max = [filas[:] for filas in hijo.get_estado()]
                alpha = max(alpha, eval)
                if beta <= alpha: break # Poda
            self.estado_solucion = [filas[:] for filas in e_max]
            return maximo
        else:
            minimo = math.inf
            hijos = self.obtener_sucesores(e, self.s_min)
            
            if not hijos: return self.calcular_heuristica(e)
            
        
            e_min = [filas[:] for filas in hijos[0].get_estado()]

            for hijo in hijos:
                eval = self.algoritmo_minimax_alpha_beta(hijo, profundidad - 1, alpha, beta, True)
                if eval < minimo:
                    minimo = eval
                    e_min = [filas[:] for filas in hijo.get_estado()]
                beta = min(beta, eval)
                if beta <= alpha: break # Poda
            self.estado_solucion = [filas[:] for filas in e_min]
            return minimo

    def inicia_busqueda(self, profundidad=4):
        self.algoritmo_minimax_alpha_beta(self.estado_inicial, profundidad, -math.inf, math.inf, True)
        print("Estados analizados por IA:", self.estados_descubiertos)
        return self.estado_solucion