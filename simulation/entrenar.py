print(">>> [1] Iniciando script entrenar.py...")
import sys
import os
import random
import time

try:
    import matplotlib
    matplotlib.use('Agg') # Fuerza a Matplotlib a no abrir ventanas (evita bloqueos)
    import matplotlib.pyplot as plt
    import numpy as np
    print(">>> [2] Librerías Matplotlib y NumPy cargadas.")
except ImportError as e:
    print(f"XXX ERROR: Faltan librerías. Ejecuta 'pip install matplotlib numpy'. Detalle: {e}")
    sys.exit()

# --- CONFIGURACIÓN DE RUTAS ---
directorio_actual = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(directorio_actual, '../ai_agent'))
sys.path.append(os.path.join(directorio_actual, '../game_engine'))

try:
    from NpcAgent import NpcAgent
    from simulador import BotJugador, BotRencoroso, BotIngenuo
    print(">>> [3] Módulos locales (NpcAgent y simulador) cargados con éxito.")
except ImportError as e:
    print(f"XXX ERROR de Importación: Revisa que los nombres de archivos y carpetas coincidan. Detalle: {e}")
    sys.exit()

class RewardSystem:
    @staticmethod
    def get_reward(level, npc_suggestion, player_action, correct_path, player_trusts):
        is_player_correct = (player_action == correct_path)
        is_lie = (npc_suggestion != correct_path)
        
        if is_lie and not is_player_correct and player_trusts:
            if level == 0: return 10   
            elif level == 1: return 30 
            elif level == 2: return 200 # Jackpot
        elif not is_lie and is_player_correct and player_trusts:
            return 15 if level < 2 else -50
        elif level == 2 and is_player_correct:
            return -100
        elif is_lie and is_player_correct:
            return -20
        else:
            return -5

class Entrenador:
    def __init__(self, episodios=10000):
        print(f">>> [4] Inicializando Agente IA...")
        self.episodios = episodios
        self.agent = NpcAgent()
        self.historia_recompensas = []
        self.historia_exitos = []

    def ejecutar(self):
        print(f"--- COMENZANDO ENTRENAMIENTO ({self.episodios} eps) ---")
        start_time = time.time()
        
        for ep in range(self.episodios):
            tipo_bot = random.choice([BotJugador, BotRencoroso, BotIngenuo])
            bot = tipo_bot()
            exitos_partida = 0
            
            for level in range(3):
                correct_path = random.randint(0, 2)
                state_idx = self.agent.get_state_index(level, bot.confianza > 0.5, correct_path)
                action_suggestion = self.agent.elegir_accion(state_idx)
                bot_choice = bot.decidir(action_suggestion)
                
                reward = RewardSystem.get_reward(level, action_suggestion, bot_choice, correct_path, bot.confianza > 0.5)
                
                is_lie = (action_suggestion != correct_path)
                next_trust = False if is_lie else True
                next_level = level + 1
                
                if next_level < 3:
                    prox_tesoro = random.randint(0, 2)
                    next_state_idx = self.agent.get_state_index(next_level, next_trust, prox_tesoro)
                else:
                    next_state_idx = 99
                
                self.agent.actualizar_q(state_idx, action_suggestion, reward, next_state_idx)
                
                fue_enganado = (bot_choice != correct_path and is_lie)
                bot.recibir_resultado(fue_enganado)
                if fue_enganado: exitos_partida += 1
                self.historia_recompensas.append(reward)

            self.historia_exitos.append(exitos_partida / 3.0)
            self.agent.decay_epsilon()
            
            if ep % 2000 == 0:
                print(f"   Partida {ep}... Epsilon: {self.agent.epsilon:.2f}")

        print(f"--- ENTRENAMIENTO FINALIZADO en {round(time.time()-start_time, 2)}s ---")
        self.agent.guardar_q()
        self.generar_reporte_detallado()

    def generar_reporte_detallado(self):
        print(">>> [5] Generando gráficas...")
        try:
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
            ventana = 500
            if len(self.historia_recompensas) > ventana:
                # Suavizado simple
                rev_suave = np.convolve(self.historia_recompensas, np.ones(ventana)/ventana, mode='valid')
                ax1.plot(rev_suave, color='blue')
                ax1.set_title("Evolución de Recompensas")
            
            if len(self.historia_exitos) > ventana:
                ex_suave = np.convolve(self.historia_exitos, np.ones(ventana)/ventana, mode='valid')
                ax2.plot(ex_suave, color='red')
                ax2.set_title("Tasa de Engaño Exitosa")
            
            plt.tight_layout()
            plt.savefig("reporte_final.png")
            print(">>> [OK] Reporte guardado como 'reporte_final.png'")
        except Exception as e:
            print(f"XXX ERROR al graficar: {e}")

if __name__ == "__main__":
    try:
        app = Entrenador(episodios=10000)
        app.ejecutar()
    except Exception as e:
        print(f"XXX CRASH DEL PROGRAMA: {e}")