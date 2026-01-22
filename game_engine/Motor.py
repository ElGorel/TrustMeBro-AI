import random
from enum import Enum

class Ubicacion(Enum):
    IZQUIERDA = 0
    CENTRO = 1
    DERECHA = 2

class EstadoJuego(Enum):
    EN_PROGRESO = "Jugando"
    GANADO = "¡Encontraste el tesoro!"
    PERDIDO = "Caíste en una trampa"

class MotorJuego:
    def __init__(self):
        self.rondas_jugadas = 0
        self.reset_ronda()

    def reset_ronda(self):
        self.estado_actual = EstadoJuego.EN_PROGRESO
        # Ahora hay 3 opciones
        opciones = [Ubicacion.IZQUIERDA, Ubicacion.CENTRO, Ubicacion.DERECHA]
        self.posicion_tesoro = random.choice(opciones)
        return self.get_info_estado()

    def evaluar_jugada(self, eleccion_jugador):
        if self.estado_actual != EstadoJuego.EN_PROGRESO:
            pass 

        if eleccion_jugador == self.posicion_tesoro:
            self.estado_actual = EstadoJuego.GANADO
        else:
            self.estado_actual = EstadoJuego.PERDIDO

        self.rondas_jugadas += 1
        return self.get_info_estado()

    def get_ubicacion_real_tesoro(self):
        return self.posicion_tesoro

    def get_info_estado(self):
        return {
            "estado": self.estado_actual,
            "tesoro_real": self.posicion_tesoro
        }