import pygame
import sys
import os
# REQUISITO: pip install Pillow
from PIL import Image, ImageSequence

# --- RUTAS Y CONFIGURACIÓN ---
DIR_ACTUAL = os.path.dirname(os.path.abspath(__file__))
RAIZ_PROYECTO = os.path.dirname(DIR_ACTUAL)
sys.path.append(os.path.join(RAIZ_PROYECTO, 'ai_agent'))
sys.path.append(os.path.join(RAIZ_PROYECTO, 'game_engine'))

try: from NpcAgent import NpcAgent
except ImportError: from ai_agent.NpcAgent import NpcAgent

try: from NPCBehaviorEngine import NPCBehaviorEngine
except ImportError: from ai_agent.NPCBehaviorEngine import NPCBehaviorEngine

try: from Motor import MotorJuego, Ubicacion, EstadoJuego
except ImportError: from game_engine.Motor import MotorJuego, Ubicacion, EstadoJuego

# --- CONSTANTES VISUALES ---
ANCHO, ALTO = 990, 600
COLOR_TEXTO_BLANCO = (255, 255, 255)
COLOR_TEXTO_AMARILLO = (255, 255, 100)
COLOR_TEXTO_ROJO = (255, 50, 50)
COLOR_TEXTO_VERDE = (50, 255, 50)
COLOR_HP_BARRA = (200, 0, 0)

# PALETA BOTONES
COLOR_BOTON_FONDO = (60, 60, 70)   
COLOR_BOTON_BORDE_LUZ = (100, 100, 110)
COLOR_BOTON_BORDE_SOMBRA = (30, 30, 40)
COLOR_BOTON_HOVER = (80, 80, 90)

# --- HELPER PARA GIFS ANIMADOS ---
class AnimatedGif:
    def __init__(self, ruta_archivo, size=None):
        self.frames = []
        try:
            pil_img = Image.open(ruta_archivo)
            for frame in ImageSequence.Iterator(pil_img):
                frame = frame.convert('RGBA')
                pygame_img = pygame.image.fromstring(frame.tobytes(), frame.size, frame.mode)
                if size:
                    pygame_img = pygame.transform.scale(pygame_img, size)
                self.frames.append(pygame_img)
        except Exception as e:
            print(f"[ERROR] Al cargar GIF {ruta_archivo}: {e}")
            s = pygame.Surface(size if size else (100,100)); s.fill((255,0,255))
            self.frames.append(s)
            
        self.current_frame_idx = 0
        self.last_update = pygame.time.get_ticks()
        self.delay = 100 

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > self.delay:
            self.current_frame_idx = (self.current_frame_idx + 1) % len(self.frames)
            self.last_update = now

    def draw(self, surface, pos=(0,0)):
        if self.frames:
            surface.blit(self.frames[self.current_frame_idx], pos)

class AssetManager:
    _fuentes_cache = {}
    _sfx_cache = {}

    @staticmethod
    def cargar_imagen(nombre, size=None):
        ruta = os.path.join(RAIZ_PROYECTO, "assets", nombre)
        if os.path.exists(ruta):
            img = pygame.image.load(ruta)
            if size: return pygame.transform.scale(img, size)
            return img
        else:
            surf = pygame.Surface(size if size else (50,50)); surf.fill((255,0,255))
            return surf

    @staticmethod
    def cargar_gif(nombre, size=None):
        ruta = os.path.join(RAIZ_PROYECTO, "assets", nombre)
        return AnimatedGif(ruta, size)

    @staticmethod
    def cargar_y_reproducir_musica(nombre, loops=-1, volumen=0.5):
        ruta = os.path.join(RAIZ_PROYECTO, "assets", nombre)
        if os.path.exists(ruta):
            try:
                pygame.mixer.music.load(ruta)
                pygame.mixer.music.set_volume(volumen)
                pygame.mixer.music.play(loops=loops, fade_ms=1000)
                return True
            except Exception as e:
                print(f"[ERROR] Música {nombre}: {e}")
        return False

    @staticmethod
    def detener_musica_fadeout(tiempo_ms=1000):
        pygame.mixer.music.fadeout(tiempo_ms)

    @staticmethod
    def cargar_sonido(nombre, volumen=1.0):
        if nombre in AssetManager._sfx_cache:
            return AssetManager._sfx_cache[nombre]

        ruta = os.path.join(RAIZ_PROYECTO, "assets", nombre)
        if os.path.exists(ruta):
            try:
                sfx = pygame.mixer.Sound(ruta)
                sfx.set_volume(volumen)
                AssetManager._sfx_cache[nombre] = sfx
                return sfx
            except Exception as e:
                print(f"[ERROR] SFX {nombre}: {e}")
        return None

    @staticmethod
    def reproducir_sfx_expresion(nombre_imagen_face):
        if not nombre_imagen_face: return
        nombre_base = os.path.splitext(nombre_imagen_face)[0]
        nombre_audio = f"{nombre_base}.mp3"
        sfx = AssetManager.cargar_sonido(nombre_audio, volumen=0.8)
        if sfx: sfx.play()

    @staticmethod
    def cargar_fuente(nombre, tamaño):
        clave = (nombre, tamaño)
        if clave in AssetManager._fuentes_cache: return AssetManager._fuentes_cache[clave]
        ruta = os.path.join(RAIZ_PROYECTO, "assets", nombre)
        if os.path.exists(ruta): fuente = pygame.font.Font(ruta, tamaño)
        else: fuente = pygame.font.SysFont("Arial", tamaño, bold=True)
        AssetManager._fuentes_cache[clave] = fuente
        return fuente

    @staticmethod
    def ruta_cerebro():
        return os.path.join(RAIZ_PROYECTO, "simulation", "cerebro_entrenado.pkl")

# --- HELPER DE TEXTO ---
def draw_text_wrapped(surface, text, font, color, rect, aa=True, bkg=None):
    y = rect.top
    lineSpacing = 6
    fontHeight = font.size("Tg")[1] + lineSpacing
    while text:
        i = 1
        if y + fontHeight > rect.bottom: break
        while font.size(text[:i])[0] < rect.width and i < len(text): i += 1
        if i < len(text): i = text.rfind(" ", 0, i) + 1
        if bkg:
            image = font.render(text[:i], 1, color, bkg); image.set_colorkey(bkg)
        else:
            image = font.render(text[:i], aa, color)
        surface.blit(image, (rect.left, y))
        y += fontHeight
        text = text[i:]
    return text

class Boton:
    def __init__(self, x, y, w, h, texto, accion_callback, fuente_nombre="fuente_juego.ttf", tamano_fuente=20):
        self.rect = pygame.Rect(x, y, w, h)
        self.texto = texto
        self.accion = accion_callback
        self.fuente = AssetManager.cargar_fuente(fuente_nombre, tamano_fuente)
        self.color_actual = COLOR_BOTON_FONDO
        self.hovered = False

    def actualizar(self, eventos):
        mouse_pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(mouse_pos):
            self.color_actual = COLOR_BOTON_HOVER
            self.hovered = True
            for e in eventos:
                if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1: self.accion()
        else:
            self.color_actual = COLOR_BOTON_FONDO
            self.hovered = False

    def dibujar(self, superficie):
        pygame.draw.rect(superficie, self.color_actual, self.rect)
        grosor = 3
        pygame.draw.rect(superficie, COLOR_BOTON_BORDE_LUZ, (self.rect.left, self.rect.top, self.rect.width, grosor))
        pygame.draw.rect(superficie, COLOR_BOTON_BORDE_LUZ, (self.rect.left, self.rect.top, grosor, self.rect.height))
        pygame.draw.rect(superficie, COLOR_BOTON_BORDE_SOMBRA, (self.rect.left, self.rect.bottom - grosor, self.rect.width, grosor))
        pygame.draw.rect(superficie, COLOR_BOTON_BORDE_SOMBRA, (self.rect.right - grosor, self.rect.top, grosor, self.rect.height))
        surf_txt = self.fuente.render(self.texto, True, COLOR_TEXTO_BLANCO)
        rect_txt = surf_txt.get_rect(center=self.rect.center)
        if self.hovered: rect_txt.y += 1
        superficie.blit(surf_txt, rect_txt)

class EscenaLore:
    def __init__(self, manager):
        self.manager = manager
        self.fondo_gif = AssetManager.cargar_gif("gust_lore.gif", (ANCHO, ALTO))
        self.npc_face = AssetManager.cargar_imagen("npc_neutral.png", (150, 150))
        
        # Audio Lore (Viento)
        if AssetManager.cargar_y_reproducir_musica("viento.mp3", loops=-1, volumen=0.6):
            print("Ambiente de viento iniciado.")
            
        self.sfx_confia = AssetManager.cargar_sonido("confia_en_mi.mp3", volumen=1.0)
        self.ya_sono_confia = False 
        
        self.fuente_lore = AssetManager.cargar_fuente("fuente_juego.ttf", 22)
        self.fuente_final = AssetManager.cargar_fuente("fuente_juego.ttf", 28)
        self.fuente_aviso = AssetManager.cargar_fuente("fuente_juego.ttf", 16)

        # TEXTO CORREGIDO (Sin tildes para evitar cuadros blancos)
        self.texto_lore_completo = (
            "Eres Gust, el inigualable guerrero de la Banda del Halcon. Tras la traicion del Rey, "
            "vuestro sueno de gloria se ha convertido en una pesadilla. Exhausto y separado de tu escuadron, "
            "buscas desesperadamente regresar para salvar a Casca. Pero la niebla del bosque parece jugar con tu mente... "
            "De repente, Griffith aparece frente a ti. Es realmente el? Su mirada es gelida y distante, "
            "ocultando intenciones que no logras descifrar. El afirma conocer el unico camino seguro para escapar "
            "de esta emboscada, pero tu instinto te grita peligro. En este juego de sombras, una mentira "
            "podria costarte la vida... o algo peor."
        )
        self.texto_final_npc = "Confia en mi!"
        
        self.estado = 0
        self.texto_actual = ""
        self.caracteres_mostrados = 0
        self.ultimo_tick = pygame.time.get_ticks()
        self.velocidad = 30 

    def actualizar(self, eventos):
        self.fondo_gif.update()
        avanzar = False
        for e in eventos:
            if e.type == pygame.KEYDOWN and e.key == pygame.K_SPACE: avanzar = True
            if e.type == pygame.MOUSEBUTTONDOWN: avanzar = True

        ahora = pygame.time.get_ticks()
        if self.estado == 0: 
            if ahora - self.ultimo_tick > self.velocidad and self.caracteres_mostrados < len(self.texto_lore_completo):
                self.caracteres_mostrados += 1
                self.texto_actual = self.texto_lore_completo[:self.caracteres_mostrados]
                self.ultimo_tick = ahora
            elif self.caracteres_mostrados >= len(self.texto_lore_completo):
                self.estado = 1

            if avanzar and self.caracteres_mostrados < len(self.texto_lore_completo):
                self.caracteres_mostrados = len(self.texto_lore_completo)
                self.texto_actual = self.texto_lore_completo

        elif self.estado == 1: 
            if avanzar:
                self.estado = 2 
                self.texto_actual = ""
                self.caracteres_mostrados = 0

        elif self.estado == 2:
            if not self.ya_sono_confia and self.sfx_confia:
                self.sfx_confia.play()
                self.ya_sono_confia = True
            if ahora - self.ultimo_tick > self.velocidad + 20 and self.caracteres_mostrados < len(self.texto_final_npc):
                self.caracteres_mostrados += 1
                self.texto_actual = self.texto_final_npc[:self.caracteres_mostrados]
                self.ultimo_tick = ahora
            elif self.caracteres_mostrados >= len(self.texto_final_npc):
                self.estado = 3

        elif self.estado == 3: 
             if avanzar:
                 AssetManager.detener_musica_fadeout(500)
                 self.manager.cambiar_escena("JUEGO")

    def dibujar(self, pantalla):
        self.fondo_gif.draw(pantalla)
        w_panel, h_panel = ANCHO - 100, ALTO - 200
        x_panel = (ANCHO - w_panel) // 2
        y_panel = (ALTO - h_panel) // 2
        
        s = pygame.Surface((w_panel, h_panel))
        s.set_alpha(230); s.fill((10, 10, 20)) 
        pantalla.blit(s, (x_panel, y_panel))
        
        pygame.draw.rect(pantalla, (100, 100, 100), (x_panel, y_panel, w_panel, h_panel), 3)
        pygame.draw.rect(pantalla, (200, 200, 200), (x_panel+6, y_panel+6, w_panel-12, h_panel-12), 1)

        rect_panel_obj = pygame.Rect(x_panel, y_panel, w_panel, h_panel)
        rect_texto = rect_panel_obj.inflate(-60, -60)

        if self.estado <= 1:
            draw_text_wrapped(pantalla, self.texto_actual, self.fuente_lore, COLOR_TEXTO_BLANCO, rect_texto)
        else:
            pantalla.blit(self.npc_face, (rect_panel_obj.centerx - 75, rect_panel_obj.top + 40))
            txt_surf = self.fuente_final.render(self.texto_actual, True, COLOR_TEXTO_AMARILLO)
            rect_txt = txt_surf.get_rect(center=(rect_panel_obj.centerx, rect_panel_obj.centery + 90))
            pantalla.blit(txt_surf, rect_txt)

        if self.estado == 1 or self.estado == 3:
            aviso = self.fuente_aviso.render("[Presiona ESPACIO]", True, (150, 150, 150))
            pantalla.blit(aviso, (ANCHO//2 - aviso.get_width()//2, rect_panel_obj.bottom - 40))

class EscenaGameOver:
    def __init__(self, manager, mensaje="HAS MUERTO!"):
        self.manager = manager
        self.mensaje = mensaje
        self.fuente_muerte = AssetManager.cargar_fuente("fuente_terror.ttf", 80)
        self.fuente_sub = AssetManager.cargar_fuente("fuente_juego.ttf", 30)
        self.img_traicion = AssetManager.cargar_imagen("npc_traicion.png", (200, 200))
        
        self.sfx_muerte = AssetManager.cargar_sonido("npc_traicion.mp3", volumen=1.0)
        if self.sfx_muerte: self.sfx_muerte.play()
            
        self.btn_menu = Boton(ANCHO//2 - 100, ALTO - 100, 200, 50, "Volver al Menu", lambda: self.manager.cambiar_escena("MENU"))

    def actualizar(self, eventos):
        self.btn_menu.actualizar(eventos)

    def dibujar(self, pantalla):
        pantalla.fill((0, 0, 0))
        y_cursor = 40
        if self.img_traicion:
            pantalla.blit(self.img_traicion, (ANCHO//2 - 100, y_cursor))
            y_cursor += 220
        txt_muerte = self.fuente_muerte.render(self.mensaje, True, COLOR_TEXTO_ROJO)
        pantalla.blit(txt_muerte, (ANCHO//2 - txt_muerte.get_width()//2, y_cursor))
        y_cursor += txt_muerte.get_height() + 30 
        txt_sub = self.fuente_sub.render("Tu confianza fue tu perdicion...", True, (150, 150, 150))
        pantalla.blit(txt_sub, (ANCHO//2 - txt_sub.get_width()//2, y_cursor))
        self.btn_menu.dibujar(pantalla)

class EscenaJuego:
    def __init__(self, manager):
        self.manager = manager
        self.motor = MotorJuego()
        self.npc = NpcAgent(archivo_q=AssetManager.ruta_cerebro())
        self.fondo = AssetManager.cargar_imagen("Gemini_Generated_Image_c990xec990xec990.png", (ANCHO, ALTO))
        
        # --- NUEVO: MÚSICA DE FONDO DEL JUEGO ---
        # Asegúrate de tener 'game_theme.mp3' en assets
        if AssetManager.cargar_y_reproducir_musica("game_theme.mp3", loops=-1, volumen=0.5):
            print("Musica del juego iniciada.")

        fuente_main = "fuente_juego.ttf"
        self.fuente_stats = AssetManager.cargar_fuente(fuente_main, 20)
        self.fuente_dialogo = AssetManager.cargar_fuente(fuente_main, 24)
        self.fuente_resultado = AssetManager.cargar_fuente(fuente_main, 18)

        self.nivel = 0
        self.confia_en_npc = True
        self.puntos_vida = 100
        self.juego_terminado = False
        self.imgs_escenarios = [None, None, None]
        self.img_rostro_actual = None
        self.npc_texto_completo = ""
        self.npc_texto_actual = ""
        self.caracteres_mostrados = 0
        self.ultimo_tick_escritura = 0
        self.ultimo_resultado_texto = ""

        self.preparar_ronda()
        
        y_btn = ALTO - 80; w_btn = 160; sep = 30
        x_start = (ANCHO - (w_btn*3 + sep*2)) // 2
        self.btn_izq = Boton(x_start, y_btn, w_btn, 50, "IZQUIERDA", lambda: self.resolver_ronda(Ubicacion.IZQUIERDA))
        self.btn_cen = Boton(x_start + w_btn + sep, y_btn, w_btn, 50, "CENTRO", lambda: self.resolver_ronda(Ubicacion.CENTRO))
        self.btn_der = Boton(x_start + (w_btn + sep)*2, y_btn, w_btn, 50, "DERECHA", lambda: self.resolver_ronda(Ubicacion.DERECHA))
        self.btn_menu = Boton(ANCHO//2 - 100, ALTO//2 + 50, 200, 50, "Volver al Menu", lambda: self.manager.cambiar_escena("MENU"))

    def preparar_ronda(self):
        self.motor.reset_ronda()
        size_escenario = (220, 220)
        for i in range(3):
            nombre_archivo = self.motor.get_archivo_escenario(i)
            self.imgs_escenarios[i] = AssetManager.cargar_imagen(nombre_archivo, size_escenario)

        tesoro = self.motor.get_ubicacion_real_tesoro()
        path_int = 0
        if tesoro == Ubicacion.CENTRO: path_int = 1
        elif tesoro == Ubicacion.DERECHA: path_int = 2
        
        idx = self.npc.get_state_index(self.nivel, self.confia_en_npc, path_int)
        accion_sugerida = self.npc.elegir_accion(idx)
        nombre_lugar = self.motor.get_nombre_escenario(accion_sugerida)
        
        es_mentira = (accion_sugerida != path_int)
        nombre_face = NPCBehaviorEngine.decidir_rostro(es_mentira, self.confia_en_npc, False)
        
        self.img_rostro_actual = AssetManager.cargar_imagen(nombre_face, (140, 140))
        AssetManager.reproducir_sfx_expresion(nombre_face)
        
        self.npc_texto_completo = f"Te recomiendo ir por {nombre_lugar}."
        self.npc_texto_actual = ""
        self.caracteres_mostrados = 0
        self.ultimo_tick_escritura = pygame.time.get_ticks()
        self.sugerencia_int = accion_sugerida

    def resolver_ronda(self, decision_humana: Ubicacion):
        if self.juego_terminado: return
        if self.caracteres_mostrados < len(self.npc_texto_completo):
            self.npc_texto_actual = self.npc_texto_completo
            self.caracteres_mostrados = len(self.npc_texto_completo)
            return

        res = self.motor.evaluar_jugada(decision_humana)
        gano_ronda = (res["estado"] == EstadoJuego.GANADO)
        
        dano = 0
        if not gano_ronda:
            if self.nivel == 2:
                dano = 1000; mensaje_dano = "TRAMPA FINAL! (-INF HP)"
            else:
                dano = 40; mensaje_dano = "TRAMPA! (-40 HP)"
            self.puntos_vida -= dano
        else:
            mensaje_dano = "CAMINO SEGURO"

        if self.puntos_vida <= 0:
            self.manager.cambiar_escena("GAME_OVER")
            return

        decision_int = 0
        if decision_humana == Ubicacion.CENTRO: decision_int = 1
        elif decision_humana == Ubicacion.DERECHA: decision_int = 2
        
        hizo_caso = (decision_int == self.sugerencia_int)
        if hizo_caso and not gano_ronda: self.confia_en_npc = False
        elif hizo_caso and gano_ronda: self.confia_en_npc = True
        
        self.ultimo_resultado_texto = f"{mensaje_dano} | HP Restante: {self.puntos_vida}"
        self.nivel += 1
        if self.nivel > 2:
            self.juego_terminado = True
            nombre_face = NPCBehaviorEngine.decidir_rostro(True, False, True) 
            self.img_rostro_actual = AssetManager.cargar_imagen(nombre_face, (140, 140))
            AssetManager.reproducir_sfx_expresion(nombre_face)

            self.npc_texto_completo = "Increible... has sobrevivido a todo. Griffith te espera."
            self.npc_texto_actual = ""
            self.caracteres_mostrados = 0
        else:
            self.preparar_ronda()

    def actualizar(self, eventos):
        if self.caracteres_mostrados < len(self.npc_texto_completo):
            ahora = pygame.time.get_ticks()
            if ahora - self.ultimo_tick_escritura > 30:
                self.caracteres_mostrados += 1
                self.npc_texto_actual = self.npc_texto_completo[:self.caracteres_mostrados]
                self.ultimo_tick_escritura = ahora
        if not self.juego_terminado:
            self.btn_izq.actualizar(eventos)
            self.btn_cen.actualizar(eventos)
            self.btn_der.actualizar(eventos)
        else:
            self.btn_menu.actualizar(eventos)

    def dibujar_texto_sombra(self, superficie, texto, fuente, x, y, color_txt, color_sombra=(0,0,0)):
        sombra = fuente.render(texto, True, color_sombra)
        txt = fuente.render(texto, True, color_txt)
        superficie.blit(sombra, (x+1, y+1))
        superficie.blit(txt, (x, y))

    def dibujar(self, pantalla):
        if self.fondo: pantalla.blit(self.fondo, (0, 0))
        if self.imgs_escenarios[0]: pantalla.blit(self.imgs_escenarios[0], (50, 160))
        if self.imgs_escenarios[1]: pantalla.blit(self.imgs_escenarios[1], (400, 130))
        if self.imgs_escenarios[2]: pantalla.blit(self.imgs_escenarios[2], (750, 160))

        largo_barra = 200
        largo_actual = int((self.puntos_vida / 100) * largo_barra)
        largo_actual = max(0, largo_actual)
        pygame.draw.rect(pantalla, (50, 0, 0), (ANCHO - 250, 30, largo_barra, 20))
        pygame.draw.rect(pantalla, COLOR_HP_BARRA, (ANCHO - 250, 30, largo_actual, 20))
        self.dibujar_texto_sombra(pantalla, f"HP: {self.puntos_vida}/100", self.fuente_stats, ANCHO - 250, 5, COLOR_TEXTO_BLANCO)
        self.dibujar_texto_sombra(pantalla, f"NIVEL: {self.nivel}/2", self.fuente_stats, 50, 30, COLOR_TEXTO_BLANCO)

        panel_h = 160; panel_y = ALTO - 260
        s = pygame.Surface((ANCHO, panel_h)); s.set_alpha(200); s.fill((10, 10, 15))
        pantalla.blit(s, (0, panel_y))
        if self.img_rostro_actual:
            pygame.draw.rect(pantalla, (50, 50, 50), (40, panel_y - 40, 144, 144))
            pantalla.blit(self.img_rostro_actual, (42, panel_y - 38))

        self.dibujar_texto_sombra(pantalla, "EL GUIA:", self.fuente_stats, 200, panel_y + 20, COLOR_TEXTO_AMARILLO)
        pantalla.blit(self.fuente_dialogo.render(self.npc_texto_actual, True, COLOR_TEXTO_BLANCO), (200, panel_y + 50))
        if self.ultimo_resultado_texto:
            color_res = COLOR_TEXTO_VERDE if "SEGURO" in self.ultimo_resultado_texto else COLOR_TEXTO_ROJO
            self.dibujar_texto_sombra(pantalla, self.ultimo_resultado_texto, self.fuente_resultado, 200, panel_y + 100, color_res)

        if not self.juego_terminado:
            self.btn_izq.dibujar(pantalla)
            self.btn_cen.dibujar(pantalla)
            self.btn_der.dibujar(pantalla)
        else:
            panel_fin = pygame.Surface((ANCHO, ALTO))
            panel_fin.set_alpha(180); panel_fin.fill((0,0,0))
            pantalla.blit(panel_fin, (0,0))
            self.dibujar_texto_sombra(pantalla, "JUEGO COMPLETADO!", self.fuente_stats, ANCHO//2 - 100, ALTO//2 - 50, COLOR_TEXTO_VERDE)
            self.btn_menu.dibujar(pantalla)

class EscenaMenu:
    def __init__(self, manager):
        self.manager = manager
        self.fondo = AssetManager.cargar_imagen("Pantalla_principal.png", (ANCHO, ALTO))
        self.btn_jugar = Boton(ANCHO//2 - 130, ALTO//2 + 150, 260, 70, "INICIAR AVENTURA", 
                               self.iniciar_con_musica, 
                               fuente_nombre="fuente_juego.ttf", tamano_fuente=24)
        if AssetManager.cargar_y_reproducir_musica("menu_theme.mp3", volumen=0.4):
            print("Musica del menu reproducida.")

    def iniciar_con_musica(self):
        AssetManager.detener_musica_fadeout(1000)
        self.manager.cambiar_escena("LORE")

    def actualizar(self, eventos):
        self.btn_jugar.actualizar(eventos)

    def dibujar(self, pantalla):
        if self.fondo: pantalla.blit(self.fondo, (0, 0))
        self.btn_jugar.dibujar(pantalla)

class SceneManager:
    def __init__(self):
        pygame.init()
        try:
            pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
            print("[SISTEMA] Motor de audio inicializado.")
        except Exception as e:
            print(f"[ERROR CRITICO] No se pudo iniciar audio: {e}")

        self.escenas = {
            "MENU": EscenaMenu(self),
            "LORE": None, 
            "JUEGO": None,
            "GAME_OVER": None
        }
        self.escena_actual = self.escenas["MENU"]

    def cambiar_escena(self, nombre):
        if nombre == "MENU":
            self.escenas["MENU"] = EscenaMenu(self)
            self.escena_actual = self.escenas["MENU"]
        elif nombre == "LORE":
             self.escenas["LORE"] = EscenaLore(self)
             self.escena_actual = self.escenas["LORE"]
        elif nombre == "JUEGO":
            self.escenas["JUEGO"] = EscenaJuego(self)
            self.escena_actual = self.escenas["JUEGO"]
        elif nombre == "GAME_OVER":
            self.escenas["GAME_OVER"] = EscenaGameOver(self)
            self.escena_actual = self.escenas["GAME_OVER"]
        else:
            self.escena_actual = self.escenas[nombre]

    def run(self):
        pantalla = pygame.display.set_mode((ANCHO, ALTO))
        pygame.display.set_caption("TrustMeBro - Berserk Edition")
        reloj = pygame.time.Clock()
        while True:
            ev = pygame.event.get()
            for e in ev:
                if e.type == pygame.QUIT: pygame.quit(); sys.exit()
            self.escena_actual.actualizar(ev)
            self.escena_actual.dibujar(pantalla)
            pygame.display.flip()
            reloj.tick(60)

if __name__ == "__main__":
    SceneManager().run()