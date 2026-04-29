class estado:
    def __init__(self, EA, EP, A, n):
        self.valor = EA      # La matriz del tablero en este estado
        self.padre = EP      # Estado padre
        self.accion = A      # Movimiento que llevó a este estado
        self.nivel = n       # Profundidad
        self.heuristica = None

    def get_estado(self):
        return self.valor

    def get_padre(self):
        return self.padre

    def get_accion(self):
        return self.accion

    def get_nivel(self):
        return self.nivel

    def get_heuristica(self):
        return self.heuristica

    def set_heuristica(self, h):
        self.heuristica = h

    def __eq__(self, e):
        return self.valor == e