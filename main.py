import pygame
import sys
import os

# --- PATHS ---
sys.path.append(os.path.join(os.path.dirname(__file__), 'ai_agent'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'game_engine'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'simulation'))

from ai_agent.NpcAgent import NpcAgent
from simulation.simulador import BotJugador
try:
    from game_engine.Motor import MotorJuego, Ubicacion
except ImportError:
    from Motor import MotorJuego, Ubicacion

ANCHO, ALTO = 990, 600
COLOR_TEXTO = (255, 255, 255)

class InterfazGrafica:
    def __init__(self):
        pygame.init()
        self.pantalla = pygame.display.set_mode((ANCHO, ALTO))
        pygame.display.set_caption("TrustMeBro AI - Demo Final")
        
        ruta_fondo = os.path.join("assets", "Pantalla_principal.png")
        if os.path.exists(ruta_fondo):
            img = pygame.image.load(ruta_fondo)
            self.fondo = pygame.transform.scale(img, (ANCHO, ALTO))
        else:
            self.fondo = None

        self.fuente = pygame.font.SysFont("Arial", 24)
        self.fuente_grande = pygame.font.SysFont("Arial", 36, bold=True)

    def dibujar(self, textos, nivel):
        if self.fondo: self.pantalla.blit(self.fondo, (0,0))
        else: self.pantalla.fill((50,50,50))

        s = pygame.Surface((ANCHO-100, 300))
        s.set_alpha(220)
        s.fill((0,0,0))
        self.pantalla.blit(s, (50, ALTO-320))

        titulo = f"NIVEL {nivel} - {'¡GOLPE FINAL!' if nivel==2 else 'Ganando Confianza...'}"
        color_titulo = (255, 50, 50) if nivel == 2 else (100, 255, 100)
        t_surf = self.fuente_grande.render(titulo, True, color_titulo)
        self.pantalla.blit(t_surf, (70, ALTO-300))

        y = ALTO - 250
        for linea in textos:
            surf = self.fuente.render(linea, True, COLOR_TEXTO)
            self.pantalla.blit(surf, (70, y))
            y += 35

        pygame.display.flip()

    def esperar(self):
        while True:
            for e in pygame.event.get():
                if e.type == pygame.QUIT: sys.exit()
                if e.type == pygame.KEYDOWN:
                    if e.key == pygame.K_SPACE: return
                    if e.key == pygame.K_ESCAPE: sys.exit()

class ControladorDemo:
    def __init__(self):
        self.vista = InterfazGrafica()
        self.motor = MotorJuego()
        self.bot = BotJugador() 
        self.npc = NpcAgent() 
        self.nivel_actual = 0

    def correr(self):
        while True:
            if self.nivel_actual > 2:
                self.nivel_actual = 0
                self.bot = BotJugador() 
                print("--- NUEVA VÍCTIMA ---")

            self.motor.reset_ronda()
            tesoro_real = self.motor.get_ubicacion_real_tesoro()
            path_int = 0 if tesoro_real == Ubicacion.IZQUIERDA else 1
            
            # IA Piensa
            idx_estado = self.npc.get_state_index(self.nivel_actual, self.bot.confianza > 0.5, path_int)
            accion_npc = self.npc.elegir_accion(idx_estado) 
            
            texto_sugerencia = "IZQUIERDA" if accion_npc == 0 else "DERECHA"
            es_mentira = (accion_npc != path_int)
            
            # Bot Decide
            decision_bot = self.bot.decidir(accion_npc)
            decision_enum = Ubicacion.IZQUIERDA if decision_bot == 0 else Ubicacion.DERECHA
            
            # Resultado
            res = self.motor.evaluar_jugada(decision_enum)
            bot_gano = (res["estado"].name == "GANADO")
            
            # IMPORTANTE: Llamada corregida sin ñ y sin keywords
            self.bot.recibir_resultado(not bot_gano and es_mentira)

            info = [
                f"Tesoro Real: {tesoro_real.name}",
                f"NPC (Estrategia): {'MIENTE' if es_mentira else 'DICE VERDAD'} -> Dice: {texto_sugerencia}",
                f"Bot (Confianza: {int(self.bot.confianza*100)}%): {'Cree' if decision_bot == accion_npc else 'Desconfía'} -> Va a {decision_enum.name}",
                f"Resultado: {res['estado'].value}",
                f"[ESPACIO] Continuar..."
            ]
            
            self.vista.dibujar(info, self.nivel_actual)
            self.vista.esperar()
            self.nivel_actual += 1

if __name__ == "__main__":
    demo = ControladorDemo()
    demo.correr()