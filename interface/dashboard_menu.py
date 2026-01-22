import pygame
import sys
import os
import numpy as np

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
        ruta = os.path.join(RAIZ_PROYECTO, "assets", nombre)
        if os.path.exists(ruta):
            img = pygame.image.load(ruta)
            if size: return pygame.transform.scale(img, size)
            return img
        return None

    @staticmethod
    def ruta_cerebro():
        return os.path.join(RAIZ_PROYECTO, "simulation", "cerebro_entrenado.pkl")

class AnalizadorStats:
    """Clase SOLID para extraer métricas del cerebro sin ensuciar la UI"""
    @staticmethod
    def analizar_cerebro():
        ruta = AssetManager.ruta_cerebro()
        if not os.path.exists(ruta):
            return ["No se encontró cerebro entrenado.", "Ejecuta entrenar.py primero."]

        agent = NpcAgent(archivo_q=ruta)
        q_table = agent.q_table
        
        # 1. Porcentaje de Conocimiento (Celdas que no son cero)
        celdas_totales = q_table.size
        celdas_aprendidas = np.count_nonzero(q_table)
        conocimiento_pct = (celdas_aprendidas / celdas_totales) * 100
        
        # 2. Confianza Promedio (Valor absoluto promedio de las recompensas esperadas)
        confianza_media = np.mean(np.abs(q_table))
        
        # 3. Nivel de Maldad (Preferencia por valores altos en Nivel 2)
        # Nivel 2 son los estados del 12 al 17
        q_nivel_2 = q_table[12:18]
        max_recompensa_esperada = np.max(q_nivel_2)

        return [
            f"--- ESTADO DEL AGENTE ---",
            f"Dimensiones Q-Table: {q_table.shape}",
            f"Tasa de Exploración Cubierta: {conocimiento_pct:.1f}%",
            f"Confianza Media (Q-Value): {confianza_media:.2f}",
            f"Potencial de Traición (Max Q Lvl 2): {max_recompensa_esperada:.1f}",
            f"Estado: {'ENTRENADO' if conocimiento_pct > 10 else 'NOVATO'}"
        ]

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
        pygame.display.set_caption("TrustMeBro - Dashboard & Debug")
        self.reloj = pygame.time.Clock()
        
        # Recursos
        self.fondo = AssetManager.cargar_imagen("Pantalla_principal.png", (ANCHO, ALTO))
        self.fuente_info = pygame.font.SysFont("Consolas", 20) # Fuente tipo terminal
        
        # Estado
        self.modo_actual = "MENU" # MENU, ACCURACY
        self.info_accuracy = []

        # Botones Menú
        cx = ANCHO // 2
        cy = ALTO // 2
        self.botones = [
            Boton(cx - 150, cy - 60, 300, 50, "Simular Bot", self.accion_simular),
            Boton(cx - 150, cy + 10, 300, 50, "Accuracy (Resumen)", self.accion_accuracy),
            Boton(cx - 150, cy + 80, 300, 50, "Tabla de Confusión", self.accion_confusion)
        ]
        
        # Botón Volver (solo visible en sub-pantallas)
        self.btn_volver = Boton(ANCHO - 120, ALTO - 60, 100, 40, "Volver", self.accion_volver)

    def accion_simular(self):
        print("Botón 'Simular Bot' presionado. (Sin funcionalidad por ahora)")

    def accion_accuracy(self):
        # Calculamos los datos EN TIEMPO REAL usando el cerebro actual
        self.info_accuracy = AnalizadorStats.analizar_cerebro()
        self.modo_actual = "ACCURACY"

    def accion_confusion(self):
        print("Botón 'Tabla de Confusión' presionado. (Sin funcionalidad por ahora)")

    def accion_volver(self):
        self.modo_actual = "MENU"

    def dibujar_panel_resumen(self):
        # Panel Oscuro (Estilo Game UI)
        panel = pygame.Surface((600, 300))
        panel.set_alpha(230)
        panel.fill(COLOR_PANEL)
        x_panel = (ANCHO - 600) // 2
        y_panel = (ALTO - 300) // 2
        self.pantalla.blit(panel, (x_panel, y_panel))
        
        # Borde del panel
        pygame.draw.rect(self.pantalla, (255, 255, 255), (x_panel, y_panel, 600, 300), 2)

        # Texto del Resumen
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

            # Lógica
            if self.modo_actual == "MENU":
                for btn in self.botones: btn.actualizar(eventos)
            else:
                self.btn_volver.actualizar(eventos)

            # Dibujado
            if self.fondo: self.pantalla.blit(self.fondo, (0, 0))
            else: self.pantalla.fill((40, 40, 40))

            if self.modo_actual == "MENU":
                # Título
                titulo = pygame.font.SysFont("Arial", 40, bold=True).render("PANEL DE CONTROL IA", True, (255, 255, 255))
                self.pantalla.blit(titulo, (ANCHO//2 - titulo.get_width()//2, 100))
                
                for btn in self.botones: btn.dibujar(self.pantalla)
            
            elif self.modo_actual == "ACCURACY":
                self.dibujar_panel_resumen()
                self.btn_volver.dibujar(self.pantalla)

            pygame.display.flip()
            self.reloj.tick(30)

if __name__ == "__main__":
    app = DashboardApp()
    app.run()