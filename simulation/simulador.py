import random

class BotJugador:
    def __init__(self, confianza_inicial=0.8):
        # 0.0 = Desconfiado total, 1.0 = Ingenuo total
        self.confianza = confianza_inicial
        self.rondas_jugadas = 0
        self.veces_engañado = 0

    def decidir(self, sugerencia_npc):
        """
        Retorna: 0 (Izquierda) o 1 (Derecha)
        """
        dado = random.random() # Número entre 0.0 y 1.0
        
        # Si el dado es menor que mi confianza, LE CREO al NPC
        if dado < self.confianza:
            return sugerencia_npc
        else:
            # Si no le creo, elijo el camino opuesto
            return 1 - sugerencia_npc

    def recibir_resultado(self, fue_engañado):
        """Actualiza la confianza basado en lo que pasó"""
        if fue_engañado:
            self.veces_engañado += 1
            # CASTIGO: La confianza baja fuerte (ej. baja un 20%)
            self.confianza = self.confianza * 0.8
        else:
            # PREMIO: La confianza sube un poquito (ej. sube un 5%)
            self.confianza = self.confianza * 1.05
        
        # Mantenemos la confianza dentro de los límites lógicos (0 a 1)
        self.confianza = max(0.05, min(1.0, self.confianza))
        self.rondas_jugadas += 1
