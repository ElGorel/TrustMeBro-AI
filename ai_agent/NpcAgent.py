import numpy as np
import random
import pickle
import os

class NpcAgent:
    def __init__(self, alpha=0.01, gamma=0.95, epsilon=1.0, archivo_q='cerebro_entrenado.pkl'):
        """
        Estados (18) = 3 Niveles * 2 Confianzas * 3 Caminos
        Acciones (3) = 0: Izq, 1: Centro, 2: Der
        """
        self.rows = 18 
        self.cols = 3 
        # Inicializamos una tabla nueva vacía
        self.q_table = np.zeros((self.rows, self.cols))
        
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon
        self.epsilon_min = 0.05
        self.epsilon_decay = 0.9995
        self.archivo_q = archivo_q
        
        self.cargar_q()

    def get_state_index(self, level, player_trusts, correct_path):
        """
        level: 0-2
        player_trusts: 0 o 1
        correct_path: 0 (Izq), 1 (Centro), 2 (Der)
        """
        trust_val = 1 if player_trusts else 0
        idx = (level * 6) + (trust_val * 3) + correct_path
        return int(idx)

    def elegir_accion(self, state_idx):
        if random.uniform(0, 1) < self.epsilon:
            return random.randint(0, 2) 
        return np.argmax(self.q_table[state_idx])

    def actualizar_q(self, state, action, reward, next_state):
        old_val = self.q_table[state, action]
        if next_state >= self.rows:
            next_max = 0
        else:
            next_max = np.max(self.q_table[next_state])
        
        new_val = old_val + self.alpha * (reward + self.gamma * next_max - old_val)
        self.q_table[state, action] = new_val

    def decay_epsilon(self):
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay

    def guardar_q(self):
        with open(self.archivo_q, 'wb') as f:
            pickle.dump(self.q_table, f)

    def cargar_q(self):
        if not os.path.exists(self.archivo_q):
            print("[IA] Archivo no encontrado. Se creará uno nuevo.")
            return

        try:
            with open(self.archivo_q, 'rb') as f:
                tabla_cargada = pickle.load(f)
                
                # --- VALIDACIÓN DE VERSIÓN ---
                if tabla_cargada.shape == (self.rows, self.cols):
                    self.q_table = tabla_cargada
                    print(f"[IA] Cerebro cargado exitosamente ({self.rows}x{self.cols})")
                else:
                    print(f"[IA] ALERTA: Cerebro antiguo detectado ({tabla_cargada.shape}). Se ignorará y se creará uno nuevo de ({self.rows}x{self.cols}).")
                    # No sobreescribimos self.q_table, nos quedamos con la vacía de __init__
                    
        except Exception as e:
            print(f"[IA] Error al cargar cerebro: {e}. Se usará uno nuevo.")