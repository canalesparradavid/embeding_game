import numpy as np

class Jugador:
    def __init__(self, nombre = "", fichas = 0):
        self.nombre = nombre
        self.fichas = fichas
        self.cartas = np.array([])