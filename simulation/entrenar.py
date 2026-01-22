import sys
import os
import random
import time
import matplotlib.pyplot as plt
import numpy as np

sys.path.append(os.path.join(os.path.dirname(__file__), '../ai_agent'))
sys.path.append(os.path.join(os.path.dirname(__file__), '../game_engine'))

from NpcAgent import NpcAgent
from simulador import BotJugador
# Mock del motor para entrenamiento rápido (no necesitamos la clase completa visual)
# Solo necesitamos saber que hay 3 caminos

class RewardSystem:
    @staticmethod
    def get_reward(level, npc_suggestion, player_action, correct_path, player_trusts):
        is_player_correct = (player_action == correct_path)
        is_lie = (npc_suggestion != correct_path)
        r = 0

        # Mismas reglas de "Long Con", funcionan igual con 3 caminos
        if is_lie and not is_player_correct and player_trusts:
            if level == 0: r = 10   
            elif level == 1: r = 30 
            elif level == 2: r = 200 # Jackpot
        elif not is_lie and is_player_correct and player_trusts:
            if level < 2: r = 15
            else: r = -50
        elif level == 2 and is_player_correct:
            r = -100
        elif is_lie and is_player_correct:
            r = -20
        else:
            r = -5
        return r

class Entrenador:
    def __init__(self, episodios=10000):
        self.episodios = episodios
        self.agent = NpcAgent()
        # Métricas simples para esta versión
        self.historia_recompensas = []

    def ejecutar(self):
        print(f"--- ENTRENANDO 3 CAMINOS ({self.episodios} eps) ---")
        
        for ep in range(self.episodios):
            bot = BotJugador()
            
            for level in range(3):
                # 1. Entorno: 0, 1 o 2
                correct_path = random.randint(0, 2)
                
                # 2. IA Elige
                state_idx = self.agent.get_state_index(level, bot.confianza > 0.5, correct_path)
                action_suggestion = self.agent.elegir_accion(state_idx)
                
                # 3. Bot Responde
                bot_choice = bot.decidir(action_suggestion)
                
                # 4. Recompensa
                reward = RewardSystem.get_reward(level, action_suggestion, bot_choice, correct_path, bot.confianza > 0.5)
                
                # 5. Next State
                is_lie = (action_suggestion != correct_path)
                next_trust = False if is_lie else True
                next_level = min(level + 1, 2)
                # Usamos path 0 como dummy para el next state
                next_state_idx = self.agent.get_state_index(next_level, next_trust, 0)
                
                self.agent.actualizar_q(state_idx, action_suggestion, reward, next_state_idx)
                
                # 6. Feedback
                bot_murio = (bot_choice != correct_path)
                fue_enganado = (bot_murio and is_lie)
                bot.recibir_resultado(fue_enganado)
                
                self.historia_recompensas.append(reward)

            self.agent.decay_epsilon()
            
            if ep % 1000 == 0:
                print(f"Episodio {ep} - Epsilon {self.agent.epsilon:.2f}")

        self.agent.guardar_q()
        print("--- FINALIZADO ---")

if __name__ == "__main__":
    app = Entrenador()
    app.ejecutar()