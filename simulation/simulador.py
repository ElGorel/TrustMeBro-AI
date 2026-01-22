import random

class BotJugador:
    def __init__(self, confianza_inicial=0.8):
        self.confianza = confianza_inicial
        self.rondas_jugadas = 0
        self.veces_enganado = 0 

    def decidir(self, sugerencia_npc):
        """
        Retorna: 0 (Izq), 1 (Centro) o 2 (Der)
        """
        dado = random.random()
        
        if dado < self.confianza:
            return sugerencia_npc # Cree en la sugerencia
        else:
            # Desconfía: Elige cualquiera MENOS la sugerida
            opciones = [0, 1, 2]
            if sugerencia_npc in opciones:
                opciones.remove(sugerencia_npc)
            return random.choice(opciones)

    def recibir_resultado(self, fue_enganado):
        if fue_enganado:
            self.veces_enganado += 1
            self.confianza *= 0.8
        else:
            self.confianza *= 1.05
        
        self.confianza = max(0.05, min(1.0, self.confianza))
        self.rondas_jugadas += 1