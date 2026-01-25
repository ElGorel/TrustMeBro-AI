import random
from enum import Enum
try:
    from ScenarioManager import ScenarioManager
except ImportError:
    from game_engine.ScenarioManager import ScenarioManager

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
        # Almacenará los objetos Escenario asignados a [0, 1, 2]
        self.escenarios_actuales = [] 
        self.reset_ronda()

    def reset_ronda(self):
        self.estado_actual = EstadoJuego.EN_PROGRESO
        
        # 1. Asignar Escenarios Visuales a las posiciones lógicas
        # indice 0 -> Escenario Izq, indice 1 -> Centro, indice 2 -> Der
        self.escenarios_actuales = ScenarioManager.obtener_escenarios_ronda(3)
        
        # 2. Lógica del Tesoro (Matemática)
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
    
    def get_nombre_escenario(self, indice_ubicacion: int) -> str:
        """Devuelve el nombre del lugar (ej: 'la Cueva') dado su índice (0,1,2)."""
        if 0 <= indice_ubicacion < len(self.escenarios_actuales):
            return self.escenarios_actuales[indice_ubicacion].id_nombre
        return "Lugar Desconocido"

    def get_archivo_escenario(self, indice_ubicacion: int) -> str:
        """Devuelve el archivo de imagen dado su índice."""
        if 0 <= indice_ubicacion < len(self.escenarios_actuales):
            return self.escenarios_actuales[indice_ubicacion].archivo_img
        return None

    def get_info_estado(self):
        return {
            "estado": self.estado_actual,
            "tesoro_real": self.posicion_tesoro
        }