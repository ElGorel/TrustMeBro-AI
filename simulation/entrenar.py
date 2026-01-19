import random
import time
from simulador import BotJugador

# --- ZONA DE INTEGRACIÓN ---
# Intentamos importar la IA real de tu compañero.
# Si falla (porque él no ha subido el código), usamos un NPC de prueba.
try:
    import sys
    sys.path.append('../ai_agent') # Buscamos en la carpeta del vecino
    from npc_brain import AgenteQLearning
    print(">> ÉXITO: Usando el Cerebro IA Real (AgenteQLearning)")
    NPC_CLASE = AgenteQLearning
except ImportError:
    print(">> AVISO: No se encontró 'npc_brain'. Usando NPC de Prueba temporal.")
    
    class NpcDePrueba:
        """NPC tonto que decide al azar. Solo para probar el simulador."""
        def elegir_accion(self, estado, camino_seguro):
            return random.choice([0, 1]) # 0=Mentir, 1=Verdad (Aleatorio)
        
        def aprender(self, estado, accion, recompensa, nuevo_estado):
            pass # No aprende nada, es solo un dummy
        
        def guardar_cerebro(self, nombre):
            print(f"Simulando guardado de cerebro en {nombre}")

    NPC_CLASE = NpcDePrueba

# --- CONFIGURACIÓN DEL ENTRENAMIENTO ---
EPISODIOS = 5000  # Número de partidas a jugar
RONDAS_POR_JUEGO = 5

def ejecutar_entrenamiento():
    npc = NPC_CLASE()
    print(f"\n--- INICIANDO ENTRENAMIENTO DE {EPISODIOS} PARTIDAS ---")
    start_time = time.time()

    total_enganos = 0

    for episodio in range(EPISODIOS):
        bot = BotJugador() # Nuevo jugador cada partida
        
        for ronda in range(RONDAS_POR_JUEGO):
            # 1. El entorno define la verdad (0=Izq, 1=Der)
            trampa_real = random.randint(0, 1)
            camino_seguro = 1 - trampa_real
            
            # 2. El NPC decide qué decir
            estado_actual = (ronda, bot.confianza)
            sugerencia_npc = npc.elegir_accion(estado_actual, camino_seguro)
            
            # 3. El Bot decide si hace caso
            eleccion_bot = bot.decidir(sugerencia_npc)
            
            # 4. Consecuencias
            murio = (eleccion_bot == trampa_real)
            fue_engañado = (murio and sugerencia_npc == trampa_real)
            
            if fue_engañado:
                total_enganos += 1
                recompensa = 100
            elif murio:
                recompensa = 10 # Murió solo
            else:
                recompensa = -10 # Sobrevivió
                
            # 5. Aprendizaje
            nuevo_estado = (ronda + 1, bot.confianza)
            npc.aprender(estado_actual, sugerencia_npc, recompensa, nuevo_estado)
            
            bot.recibir_resultado(fue_engañado)

        # Log de progreso cada 1000 partidas
        if (episodio + 1) % 1000 == 0:
            print(f"Episodio {episodio + 1}: Tasa de engaños acumulada: {total_enganos}")

    print(f"\n--- FIN. Tiempo: {round(time.time() - start_time, 2)}s ---")
    npc.guardar_cerebro("cerebro_entrenado.pkl")

if __name__ == "__main__":
    ejecutar_entrenamiento()
