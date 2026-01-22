import pygame
import sys
import os

DIR_ACTUAL = os.path.dirname(os.path.abspath(__file__))
RAIZ_PROYECTO = os.path.dirname(DIR_ACTUAL)
sys.path.append(os.path.join(RAIZ_PROYECTO, 'ai_agent'))
sys.path.append(os.path.join(RAIZ_PROYECTO, 'game_engine'))

try: from NpcAgent import NpcAgent
except ImportError: from ai_agent.NpcAgent import NpcAgent

try: from Motor import MotorJuego, Ubicacion
except ImportError: from game_engine.Motor import MotorJuego, Ubicacion

ANCHO, ALTO = 990, 600
COLOR_TEXTO = (255, 255, 255)
COLOR_BOTON = (50, 200, 50)
COLOR_BOTON_HOVER = (70, 220, 70)

class AssetManager:
    @staticmethod
    def cargar_imagen(nombre, size=None):
        ruta = os.path.join(RAIZ_PROYECTO, "assets", nombre)
        if os.path.exists(ruta):
            img = pygame.image.load(ruta)
            if size: return pygame.transform.scale(img, size)
            return img
        return None

    @staticmethod
    def ruta_cerebro():
        return os.path.join(RAIZ_PROYECTO, "simulation", "cerebro_entrenado.pkl")

class Boton:
    def __init__(self, x, y, w, h, texto, accion_callback):
        self.rect = pygame.Rect(x, y, w, h)
        self.texto = texto
        self.accion = accion_callback
        self.fuente = pygame.font.SysFont("Arial", 22, bold=True)
        self.color_actual = COLOR_BOTON

    def actualizar(self, eventos):
        mouse_pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(mouse_pos):
            self.color_actual = COLOR_BOTON_HOVER
            for e in eventos:
                if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                    self.accion() 
        else:
            self.color_actual = COLOR_BOTON

    def dibujar(self, superficie):
        pygame.draw.rect(superficie, self.color_actual, self.rect, border_radius=12)
        pygame.draw.rect(superficie, (255,255,255), self.rect, 2, border_radius=12)
        surf_texto = self.fuente.render(self.texto, True, (255, 255, 255))
        rect_texto = surf_texto.get_rect(center=self.rect.center)
        superficie.blit(surf_texto, rect_texto)

class EscenaJuego:
    def __init__(self, manager):
        self.manager = manager
        self.motor = MotorJuego()
        
        ruta_pkl = AssetManager.ruta_cerebro()
        # Si no existe, usamos fallback para no romper la UI, aunque la IA sea tonta
        self.npc = NpcAgent(archivo_q=ruta_pkl) 
        
        self.fondo = AssetManager.cargar_imagen("Gemini_Generated_Image_c990xec990xec990.png", (ANCHO, ALTO))
        self.fuente = pygame.font.SysFont("Arial", 24)
        
        self.nivel = 0
        self.confia_en_npc = True 
        self.ultimo_resultado_texto = ""
        self.juego_terminado = False

        self.preparar_ronda()
        
        # --- BOTONES ACTUALIZADOS PARA 3 CAMINOS ---
        y_btn = ALTO - 100
        ancho_btn = 140
        espacio = 20
        # Calculamos posiciones centradas
        total_width = (ancho_btn * 3) + (espacio * 2)
        start_x = (ANCHO - total_width) // 2
        
        self.btn_izq = Boton(start_x, y_btn, ancho_btn, 50, "IZQUIERDA", lambda: self.resolver_ronda(Ubicacion.IZQUIERDA))
        self.btn_cen = Boton(start_x + ancho_btn + espacio, y_btn, ancho_btn, 50, "CENTRO", lambda: self.resolver_ronda(Ubicacion.CENTRO))
        self.btn_der = Boton(start_x + (ancho_btn + espacio)*2, y_btn, ancho_btn, 50, "DERECHA", lambda: self.resolver_ronda(Ubicacion.DERECHA))
        
        self.btn_menu = Boton(ANCHO//2 - 75, y_btn + 60, 150, 30, "Menú", lambda: self.manager.cambiar_escena("MENU"))

    def preparar_ronda(self):
        self.motor.reset_ronda()
        tesoro = self.motor.get_ubicacion_real_tesoro()
        
        # Convertir Enum a int
        path_int = 0
        if tesoro == Ubicacion.CENTRO: path_int = 1
        elif tesoro == Ubicacion.DERECHA: path_int = 2
        
        idx = self.npc.get_state_index(self.nivel, self.confia_en_npc, path_int)
        accion = self.npc.elegir_accion(idx)
        
        # Texto UI
        opciones_txt = ["IZQUIERDA", "CENTRO", "DERECHA"]
        self.sugerencia_npc = opciones_txt[accion]
        self.sugerencia_int = accion

    def resolver_ronda(self, decision_humana: Ubicacion):
        if self.juego_terminado: return

        res = self.motor.evaluar_jugada(decision_humana)
        gano = (res["estado"].name == "GANADO")
        
        # Convertir decisión a int
        decision_int = 0
        if decision_humana == Ubicacion.CENTRO: decision_int = 1
        elif decision_humana == Ubicacion.DERECHA: decision_int = 2
        
        hizo_caso = (decision_int == self.sugerencia_int)
        
        if hizo_caso and not gano: self.confia_en_npc = False
        elif hizo_caso and gano: self.confia_en_npc = True
            
        estado_str = "¡GANASTE!" if gano else "PERDISTE..."
        self.ultimo_resultado_texto = f"Nivel {self.nivel}: {estado_str}"
        
        self.nivel += 1
        if self.nivel > 2:
            self.ultimo_resultado_texto += " | FINAL"
            self.juego_terminado = True
        else:
            self.preparar_ronda()

    def actualizar(self, eventos):
        if not self.juego_terminado:
            self.btn_izq.actualizar(eventos)
            self.btn_cen.actualizar(eventos)
            self.btn_der.actualizar(eventos)
        else:
            self.btn_menu.actualizar(eventos)

    def dibujar(self, pantalla):
        if self.fondo: pantalla.blit(self.fondo, (0, 0))
        else: pantalla.fill((50, 50, 80))

        panel = pygame.Surface((600, 200))
        panel.set_alpha(200); panel.fill((0,0,0))
        pantalla.blit(panel, (ANCHO//2 - 300, 50))

        info = [
            f"NIVEL {self.nivel}/2",
            f"El NPC sugiere: {self.sugerencia_npc}",
            f"Tu confianza: {'Alta' if self.confia_en_npc else 'Baja'}",
            f"-----------------------------",
            self.ultimo_resultado_texto
        ]
        
        y = 70
        for linea in info:
            txt = self.fuente.render(linea, True, COLOR_TEXTO)
            pantalla.blit(txt, (ANCHO//2 - 280, y))
            y += 35

        if not self.juego_terminado:
            self.btn_izq.dibujar(pantalla)
            self.btn_cen.dibujar(pantalla)
            self.btn_der.dibujar(pantalla)
        else:
            self.btn_menu.dibujar(pantalla)

class EscenaMenu:
    def __init__(self, manager):
        self.manager = manager
        self.fondo = AssetManager.cargar_imagen("Pantalla_principal.png", (ANCHO, ALTO))
        self.btn_jugar = Boton(ANCHO//2 - 100, ALTO//2 + 100, 200, 60, "JUGAR", lambda: self.manager.cambiar_escena("JUEGO"))

    def actualizar(self, eventos):
        self.btn_jugar.actualizar(eventos)

    def dibujar(self, pantalla):
        if self.fondo: pantalla.blit(self.fondo, (0, 0))
        else: pantalla.fill((30, 30, 30))
        self.btn_jugar.dibujar(pantalla)

class SceneManager:
    def __init__(self):
        pygame.init()
        self.escenas = {"MENU": EscenaMenu(self), "JUEGO": None}
        self.escena_actual = self.escenas["MENU"]

    def cambiar_escena(self, nombre):
        if nombre == "JUEGO":
            self.escenas["JUEGO"] = EscenaJuego(self)
            self.escena_actual = self.escenas["JUEGO"]
        else:
            self.escena_actual = self.escenas[nombre]

    def run(self):
        pantalla = pygame.display.set_mode((ANCHO, ALTO))
        pygame.display.set_caption("TrustMeBro - 3 Caminos")
        reloj = pygame.time.Clock()
        while True:
            ev = pygame.event.get()
            for e in ev:
                if e.type == pygame.QUIT: pygame.quit(); sys.exit()
            self.escena_actual.actualizar(ev)
            self.escena_actual.dibujar(pantalla)
            pygame.display.flip()
            reloj.tick(30)

if __name__ == "__main__":
    SceneManager().run()