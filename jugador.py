from busqueda import busqueda

class jugador:
    def __init__(self, nombre, tipo):
        self.nombre = nombre
        self.es_bot = tipo
        self.simbolo = None

    def set_simbolo(self, simbolo):
        self.simbolo = simbolo # 'b' o 'n'

    def toma_turno_automatico(self, matriz, simbolo):
        # Configurar quién es max y min para el bot
        s_max = simbolo
        s_min = 'n' if simbolo == 'b' else 'b'

        bot = busqueda(matriz, s_max, s_min)
        # Inicia búsqueda con profundidad 4 
        nueva_matriz = bot.inicia_busqueda(4) 
        return nueva_matriz
        
    def toma_turno_por_teclado(self, matriz, simbolo):
        print("Ingresa las coordenadas de la pieza a mover y su destino.")
        
        while True:
            try:
                f_origen = int(input("Fila origen [0-7]: "))
                c_origen = int(input("Columna origen [0-7]: "))
                f_destino = int(input("Fila destino [0-7]: "))
                c_destino = int(input("Columna destino [0-7]: "))
                
                pieza = matriz[f_origen][c_origen]
                if pieza.lower() == simbolo:
                    # Aplicar movimiento básico
                    matriz[f_destino][c_destino] = pieza
                    matriz[f_origen][c_origen] = " "
                    
                    # Coronación básica humana 
                    if simbolo == 'b' and f_destino == 0: matriz[f_destino][c_destino] = 'B'
                    if simbolo == 'n' and f_destino == 7: matriz[f_destino][c_destino] = 'N'
                    
                    # Si fue salto, eliminar pieza capturada 
                    if abs(f_destino - f_origen) == 2:
                        f_medio = (f_origen + f_destino) // 2
                        c_medio = (c_origen + c_destino) // 2
                        matriz[f_medio][c_medio] = " "
                    break
                else:
                    print("Esa no es tu pieza. Intenta de nuevo.")
            except:
                print("Entrada inválida. Usa números del 0 al 7.")

        return matriz

    def toma_turno(self, matriz, simbolo):
        if self.es_bot:
            return self.toma_turno_automatico(matriz, simbolo)
        return self.toma_turno_por_teclado(matriz, simbolo)