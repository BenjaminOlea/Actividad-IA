class tablero:
    def __init__(self, jugador1, jugador2):
        self.jugador1 = jugador1
        self.jugador1.set_simbolo('b') # 'b' para peón, 'B' para Dama
        self.jugador2 = jugador2
        self.jugador2.set_simbolo('n') # 'n' para peón, 'N' para Dama
        self.hay_ganador = False
        self.matriz = []
        self.iniciar_matriz()

    def iniciar_matriz(self):
        # Tablero 8x8 vacío
        self.matriz = [[" " for _ in range(8)] for _ in range(8)]
        # Colocar 12 piezas del jugador 2 
        for fila in range(3):
            for col in range(8):
                if (fila + col) % 2 != 0:
                    self.matriz[fila][col] = 'n'
        # Colocar 12 piezas del jugador 1 
        for fila in range(5, 8):
            for col in range(8):
                if (fila + col) % 2 != 0:
                    self.matriz[fila][col] = 'b'

    def insertar_movimiento(self, matriz):
        self.matriz = matriz

    def imprimir_matriz(self):
        print("\n  0   1   2   3   4   5   6   7")
        print("  ---------------------------------")
        for i in range(8):
            fila_str = str(i) + " | "
            for j in range(8):
                fila_str += self.matriz[i][j] + " | "
            print(fila_str)
            print("  ---------------------------------")

    def contar_piezas(self):
        b = 0
        n = 0
        for fila in range(8):
            for col in range(8):
                if self.matriz[fila][col] in ['b', 'B']: b += 1
                elif self.matriz[fila][col] in ['n', 'N']: n += 1
        return b, n

    def inicia_partida(self):
        print("************ INICIA PARTIDA DE DAMAS ************")
        limite_turnos = 100 # Evitar bucles infinitos
        i = 1

        while i <= limite_turnos:
            self.imprimir_matriz()
            b, n = self.contar_piezas()
            if b == 0 or n == 0:
                self.hay_ganador = True
                break

            if i % 2 != 0:
                print(f"\nTurno de {self.jugador1.nombre} (Blancas 'b')")
                nueva_matriz = self.jugador1.toma_turno(self.matriz, 'b')
            else:
                print(f"\nTurno de {self.jugador2.nombre} (Negras 'n')")
                nueva_matriz = self.jugador2.toma_turno(self.matriz, 'n')
            
            self.insertar_movimiento(nueva_matriz)
            i += 1
        
        self.imprimir_matriz()
        b, n = self.contar_piezas()
        if b == 0:
            print(f"\nGanador: {self.jugador2.nombre}!")
        elif n == 0:
            print(f"\nGanador: {self.jugador1.nombre}!")
        else:
            print("\nEmpate o límite de turnos alcanzado.")
        print("************ FIN DE PARTIDA ************")