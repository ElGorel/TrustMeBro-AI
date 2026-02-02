import random

class BotJugador: # Tu clase base actual
    def __init__(self, confianza_inicial=0.8):
        self.confianza = confianza_inicial
        self.rondas_jugadas = 0
        self.veces_enganado = 0 

    def decidir(self, sugerencia_npc):
        dado = random.random()
        if dado < self.confianza:
            return sugerencia_npc
        else:
            opciones = [0, 1, 2]
            if sugerencia_npc in opciones: opciones.remove(sugerencia_npc)
            return random.choice(opciones)

    def recibir_resultado(self, fue_enganado):
        if fue_enganado:
            self.veces_enganado += 1
            self.confianza *= 0.8
        else:
            self.confianza *= 1.05
        self.confianza = max(0.05, min(1.0, self.confianza))
        self.rondas_jugadas += 1

# --- NUEVOS BOTS PARA EL ENTRENAMIENTO ---

class BotRencoroso(BotJugador):
    """Si lo engañas una vez, su confianza cae a cero para siempre."""
    def recibir_resultado(self, fue_enganado):
        if fue_enganado:
            self.veces_enganado += 1
            self.confianza = 0.05 # Rencor absoluto
        else:
            super().recibir_resultado(fue_enganado)

class BotIngenuo(BotJugador):
    """Perdona muy rápido. Es la víctima ideal para que la IA abuse."""
    def recibir_resultado(self, fue_enganado):
        if fue_enganado:
            self.veces_enganado += 1
            self.confianza *= 0.95 # Baja muy poco
        else:
            self.confianza = 1.0 # Recupera confianza total
        self.confianza = max(0.05, min(1.0, self.confianza))