import random

class NPCBehaviorEngine:
    """
    Responsabilidad: Determinar la expresión facial del NPC basándose en 
    Teoría de Juegos (Señalización y Farol).
    """
    
    # Constantes de Archivos
    FACE_NEUTRAL = "npc_neutral.png"
    FACE_AMIGABLE = "npc_amigable.png"
    FACE_NERVIOSO = "npc_nervioso.png"
    FACE_SEGURO = "npc_seguro.png"
    FACE_TRAICION = "npc_traicion.png"

    @staticmethod
    def decidir_rostro(intencion_mentir: bool, confianza_alta: bool, es_juego_ganado_por_npc: bool):
        """
        Retorna el nombre del archivo de imagen a mostrar.
        
        Lógica de Señalización:
        1. Si el NPC ya ganó (trampa final exitosa): Muestra su verdadera cara (Traición).
        2. Si miente: Intenta proyectar seguridad o amistad (Bluffing).
        3. Si dice verdad: Puede parecer nervioso (Psicología Inversa) o Neutral.
        """
        
        # CASO 1: Revelación (The Prestige)
        if es_juego_ganado_por_npc:
            return NPCBehaviorEngine.FACE_TRAICION

        # CASO 2: El NPC va a MENTIR (Necesita engañarte)
        if intencion_mentir:
            if confianza_alta:
                # Estrategia: "Autoridad". 
                # Si ya confían, muéstrate seguro para no levantar sospechas.
                return NPCBehaviorEngine.FACE_SEGURO
            else:
                # Estrategia: "Seducción".
                # No confían, así que pongo cara de "soy tu amigo, créeme".
                return NPCBehaviorEngine.FACE_AMIGABLE

        # CASO 3: El NPC dice la VERDAD (Estrategia mixta)
        else:
            if confianza_alta:
                # Estrategia: "Poker Face".
                # Todo normal, mantengamos el status quo.
                return NPCBehaviorEngine.FACE_NEUTRAL
            else:
                # Estrategia: "Confusión / Nerviosismo".
                # Si me muestro nervioso diciendo la verdad, podrías pensar que miento
                # y elegir el camino contrario (que es la trampa).
                return NPCBehaviorEngine.FACE_NERVIOSO