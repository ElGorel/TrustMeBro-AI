import pygame
import sys
import os
import numpy as np
import subprocess # Necesario para abrir main.py como proceso aparte

# --- CONFIGURACIÓN DE RUTAS ---
DIR_ACTUAL = os.path.dirname(os.path.abspath(__file__))
RAIZ_PROYECTO = os.path.dirname(DIR_ACTUAL)
sys.path.append(os.path.join(RAIZ_PROYECTO, 'ai_agent'))
sys.path.append(os.path.join(RAIZ_PROYECTO, 'game_engine'))

# --- IMPORTS ---
try: from NpcAgent import NpcAgent
except ImportError: from ai_agent.NpcAgent import NpcAgent

# --- CONSTANTES ---
ANCHO, ALTO = 990, 600
COLOR_TEXTO = (255, 255, 255)
COLOR_BOTON = (70, 130, 180) # Azul Acero
COLOR_BOTON_HOVER = (100, 149, 237)
COLOR_PANEL = (0, 0, 0)

class AssetManager:
    @staticmethod
    def cargar_imagen(nombre, size=None):
        # Busca primero en la raíz (donde se guarda el reporte usualmente)
        ruta_root = os.path.join(RAIZ_PROYECTO, nombre)
        # Busca en assets
        ruta_assets = os.path.join(RAIZ_PROYECTO, "assets", nombre)
        # Busca en simulation
        ruta_sim = os.path.join(RAIZ_PROYECTO, "simulation", nombre)

        ruta_final = None
        if os.path.exists(ruta_root): ruta_final = ruta_root
        elif os.path.exists(ruta_assets): ruta_final = ruta_assets
        elif os.path.exists(ruta_sim): ruta_final = ruta_sim

        if ruta_final:
            try:
                img = pygame.image.load(ruta_final)
                if size: return pygame.transform.scale(img, size)
                return img
            except:
                return None
        return None

    @staticmethod
    def ruta_cerebro():
        return os.path.join(RAIZ_PROYECTO, "simulation", "cerebro_entrenado.pkl")

class AnalizadorStats:
    @staticmethod
    def analizar_cerebro():
        ruta = AssetManager.ruta_cerebro()
        if not os.path.exists(ruta):
            return ["No se encontró cerebro entrenado.", "Ejecuta entrenar.py primero."]

        try:
            agent = NpcAgent(archivo_q=ruta)
            q_table = agent.q_table
            
            celdas_totales = q_table.size
            celdas_aprendidas = np.count_nonzero(q_table)
            conocimiento_pct = (celdas_aprendidas / celdas_totales) * 100
            confianza_media = np.mean(np.abs(q_table))
            
            q_nivel_2 = q_table[12:18]
            max_recompensa_esperada = np.max(q_nivel_2)

            return [
                f"--- ESTADO DEL AGENTE ---",
                f"Dimensiones Q-Table: {q_table.shape}",
                f"Tasa de Exploración: {conocimiento_pct:.1f}%",
                f"Confianza Media (Q): {confianza_media:.2f}",
                f"Potencial Traición (Max Lvl 2): {max_recompensa_esperada:.1f}",
                f"Estado: {'ENTRENADO' if conocimiento_pct > 10 else 'NOVATO'}"
            ]
        except Exception as e:
            return [f"Error al leer cerebro: {str(e)}"]

class Boton:
    def __init__(self, x, y, w, h, texto, callback):
        self.rect = pygame.Rect(x, y, w, h)
        self.texto = texto
        self.callback = callback
        self.fuente = pygame.font.SysFont("Arial", 20, bold=True)
        self.color = COLOR_BOTON

    def actualizar(self, eventos):
        mouse_pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(mouse_pos):
            self.color = COLOR_BOTON_HOVER
            for e in eventos:
                if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                    self.callback()
        else:
            self.color = COLOR_BOTON

    def dibujar(self, pantalla):
        pygame.draw.rect(pantalla, self.color, self.rect, border_radius=8)
        pygame.draw.rect(pantalla, (255,255,255), self.rect, 2, border_radius=8)
        surf = self.fuente.render(self.texto, True, (255, 255, 255))
        rect = surf.get_rect(center=self.rect.center)
        pantalla.blit(surf, rect)

class DashboardApp:
    def __init__(self):
        pygame.init()
        self.pantalla = pygame.display.set_mode((ANCHO, ALTO))
        pygame.display.set_caption("TrustMeBro - Dashboard Manager")
        self.reloj = pygame.time.Clock()
        
        self.fondo = AssetManager.cargar_imagen("Pantalla_principal.png", (ANCHO, ALTO))
        self.fuente_info = pygame.font.SysFont("Consolas", 20)
        
        self.modo_actual = "MENU" # MENU, ACCURACY, RESUMEN
        self.info_accuracy = []
        self.img_reporte = None

        cx, cy = ANCHO // 2, ALTO // 2
        
        # --- BOTONES ACTUALIZADOS ---
        self.botones = [
            Boton(cx - 150, cy - 60, 300, 50, "Simular Bot (Demo)", self.accion_simular),
            Boton(cx - 150, cy + 10, 300, 50, "Accuracy (Datos Q-Table)", self.accion_accuracy),
            Boton(cx - 150, cy + 80, 300, 50, "Resumen (Gráfica)", self.accion_resumen)
        ]
        
        self.btn_volver = Boton(ANCHO - 120, ALTO - 60, 100, 40, "Volver", self.accion_volver)

    def accion_simular(self):
        """Lanza main.py como un proceso externo para no bloquear el dashboard"""
        ruta_main = os.path.join(RAIZ_PROYECTO, "main.py")
        if os.path.exists(ruta_main):
            print("Lanzando simulación...")
            try:
                # sys.executable asegura que usemos el mismo python que corre esto
                subprocess.Popen([sys.executable, ruta_main])
            except Exception as e:
                print(f"Error al lanzar simulación: {e}")
        else:
            print("No se encontró main.py")

    def accion_accuracy(self):
        self.info_accuracy = AnalizadorStats.analizar_cerebro()
        self.modo_actual = "ACCURACY"

    def accion_resumen(self):
        # Intentamos cargar 'reporte_final.png' o el generado 'reporte_aprendizaje.png'
        # Buscamos primero el nombre que pediste, luego el fallback
        self.img_reporte = AssetManager.cargar_imagen("reporte_final.png")
        
        if not self.img_reporte:
             # Si no existe, buscamos el que genera entrenar.py por defecto
             self.img_reporte = AssetManager.cargar_imagen("reporte_aprendizaje.png")
        
        if self.img_reporte:
            # Escalar imagen si es muy grande para que quepa
            # Mantenemos aspect ratio o forzamos ajuste suave
            self.img_reporte = pygame.transform.scale(self.img_reporte, (800, 450))
            
        self.modo_actual = "RESUMEN"

    def accion_volver(self):
        self.modo_actual = "MENU"

    def dibujar_panel_resumen(self):
        # Título
        titulo = pygame.font.SysFont("Arial", 24, bold=True).render("REPORTE DE APRENDIZAJE", True, (255, 255, 100))
        self.pantalla.blit(titulo, (ANCHO//2 - titulo.get_width()//2, 30))

        if self.img_reporte:
            # Centrar imagen
            x_img = (ANCHO - 800) // 2
            y_img = (ALTO - 450) // 2 + 20
            
            # Marco
            pygame.draw.rect(self.pantalla, (255, 255, 255), (x_img-5, y_img-5, 810, 460), 2)
            self.pantalla.blit(self.img_reporte, (x_img, y_img))
        else:
            # Mensaje de error si no hay imagen
            msg = self.fuente_info.render("No se encontró 'reporte_final.png' ni 'reporte_aprendizaje.png'", True, (255, 100, 100))
            self.pantalla.blit(msg, (ANCHO//2 - msg.get_width()//2, ALTO//2))
            msg2 = self.fuente_info.render("Ejecuta 'entrenar.py' para generar la gráfica.", True, (200, 200, 200))
            self.pantalla.blit(msg2, (ANCHO//2 - msg2.get_width()//2, ALTO//2 + 30))

    def dibujar_panel_accuracy(self):
        panel = pygame.Surface((600, 300))
        panel.set_alpha(230)
        panel.fill(COLOR_PANEL)
        x_panel = (ANCHO - 600) // 2
        y_panel = (ALTO - 300) // 2
        self.pantalla.blit(panel, (x_panel, y_panel))
        pygame.draw.rect(self.pantalla, (255, 255, 255), (x_panel, y_panel, 600, 300), 2)

        y_text = y_panel + 40
        for linea in self.info_accuracy:
            surf = self.fuente_info.render(linea, True, COLOR_TEXTO)
            self.pantalla.blit(surf, (x_panel + 40, y_text))
            y_text += 35

    def run(self):
        while True:
            eventos = pygame.event.get()
            for e in eventos:
                if e.type == pygame.QUIT: pygame.quit(); sys.exit()

            if self.modo_actual == "MENU":
                for btn in self.botones: btn.actualizar(eventos)
            else:
                self.btn_volver.actualizar(eventos)

            if self.fondo: self.pantalla.blit(self.fondo, (0, 0))
            else: self.pantalla.fill((40, 40, 40))

            if self.modo_actual == "MENU":
                t = pygame.font.SysFont("Arial", 40, bold=True).render("PANEL DE CONTROL IA", True, (255, 255, 255))
                self.pantalla.blit(t, (ANCHO//2 - t.get_width()//2, 100))
                for btn in self.botones: btn.dibujar(self.pantalla)
            
            elif self.modo_actual == "ACCURACY":
                self.dibujar_panel_accuracy()
                self.btn_volver.dibujar(self.pantalla)
            
            elif self.modo_actual == "RESUMEN":
                self.dibujar_panel_resumen()
                self.btn_volver.dibujar(self.pantalla)

            pygame.display.flip()
            self.reloj.tick(30)

if __name__ == "__main__":
    app = DashboardApp()
    app.run()