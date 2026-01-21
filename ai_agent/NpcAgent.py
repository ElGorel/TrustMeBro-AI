import numpy as np
import pickle
import random


class NpcAgent:
    # Constantes de recompensa (las movemos al inicio de la clase)
    RECOMPENSA_MENTIRA_EXITOSA     = 100
    RECOMPENSA_MENTIRA_DESCUBIERTA = -50
    RECOMPENSA_VERDAD_ESTRATEGICA  = -5
    RECOMPENSA_POR_DEFECTO         = -1     # pequeño castigo por tiempo perdido
    RECOMPENSA_TIEMPO_PERDIDO      = -2
    RECOMPENSA_JUGADOR_ENCONTRO    = -200   # castigo fuerte si encuentra el tesoro

    def __init__(self, alpha=0.1, gamma=0.9, epsilon=0.1, estados=5, acciones=5, archivo_q='q_table.pkl'):
        """
        Inicializa el agente Q-learning.
        - alpha: tasa de aprendizaje
        - gamma: factor de descuento
        - epsilon: tasa de exploración
        - estados: número de estados (5)
        - acciones: número de acciones (5)
        - archivo_q: nombre del archivo para guardar/cargar la tabla Q
        """
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon
        self.estados = estados
        self.acciones = acciones
        self.archivo_q = archivo_q

        # Inicializa la tabla Q con ceros
        self.Q = np.zeros((estados, acciones))

        # Intenta cargar la tabla Q si existe
        self.cargar_q()

    def elegir_accion(self, estado):
        """
        Elige una acción usando epsilon-greedy.
        - estado: estado actual (entero de 0 a 4)
        Retorna: acción elegida (entero de 0 a 4)
        """
        if random.random() < self.epsilon:
         return random.randint(0, self.acciones - 1)
        else:
         max_q = np.max(self.Q[estado])
         acciones_max = np.where(self.Q[estado] == max_q)[0]
         return random.choice(acciones_max)

    def actualizar_q(self, estado, accion, recompensa, estado_siguiente):
        """
        Actualiza la tabla Q usando la fórmula de Q-learning.
        Q(s,a) ← Q(s,a) + α [r + γ·maxQ(s',a') − Q(s,a)]
        """
        max_q_siguiente = np.max(self.Q[estado_siguiente])
        self.Q[estado, accion] += self.alpha * (recompensa + self.gamma * max_q_siguiente - self.Q[estado, accion])

    def get_recompensa(self, tipo_evento: str) -> float:
        """
        Devuelve la recompensa según el tipo de evento.
        Uso recomendado:
            recompensa = agente.get_recompensa("mentira_exitosa")
            agente.actualizar_q(estado, accion, recompensa, estado_siguiente)
        """
        recompensas = {
            "mentira_exitosa":     self.RECOMPENSA_MENTIRA_EXITOSA,
            "mentira_descubierta": self.RECOMPENSA_MENTIRA_DESCUBIERTA,
            "verdad_estrategica":  self.RECOMPENSA_VERDAD_ESTRATEGICA,
            "default":             self.RECOMPENSA_POR_DEFECTO,
            "tiempo_perdido":      self.RECOMPENSA_TIEMPO_PERDIDO,
            "jugador_encontro":    self.RECOMPENSA_JUGADOR_ENCONTRO,
        }
        return recompensas.get(tipo_evento, self.RECOMPENSA_POR_DEFECTO)

    def guardar_q(self):
        """ Guarda la tabla Q usando pickle """
        with open(self.archivo_q, 'wb') as f:
            pickle.dump(self.Q, f)

    def cargar_q(self):
        """ Carga la tabla Q si existe """
        try:
            with open(self.archivo_q, 'rb') as f:
                self.Q = pickle.load(f)
                print(f"Tabla Q cargada desde {self.archivo_q}")
        except FileNotFoundError:
            print(f"Archivo {self.archivo_q} no encontrado. Usando tabla Q inicial (ceros).")


# Ejemplo de uso rápido (opcional, para verificar)
if __name__ == "__main__":
    agente = NpcAgent(estados=5, acciones=5)
    print("Tabla Q inicial:")
    print(agente.Q)

    # Simula una actualización
    agente.actualizar_q(estado=0, accion=2, recompensa=100, estado_siguiente=1)
    print("\nDespués de una actualización:")
    print(agente.Q)

    print("\nRecompensa ejemplo:", agente.get_recompensa("mentira_exitosa"))
