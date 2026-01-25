from dataclasses import dataclass
import random

@dataclass
class Escenario:
    """DTO (Data Transfer Object) para representar un lugar."""
    id_nombre: str       # Para mostrar en texto (ej: "la Cueva")
    archivo_img: str     # Nombre del archivo (ej: "cueva.png")

class ScenarioManager:
    """
    Responsabilidad: Proveer escenarios aleatorios y gestionar sus metadatos.
    """
    # Base de datos estática de lugares disponibles
    _LUGARES_DISPONIBLES = [
        Escenario("el Campamento", "campamento.png"),
        Escenario("el Campamento Base", "campamento2.png"),
        Escenario("la Casa Abandonada", "casa_abandonada.png"),
        Escenario("el Cementerio", "cementerio.png"),
        Escenario("la Cueva de Lobos", "cueva_de_lobos.png"),
        Escenario("la Cueva Oscura", "cueva.png"),
        Escenario("el Edificio en Ruinas", "edificio_abandonado.png"),
        Escenario("la Estatua Antigua", "estatua.png"),
        Escenario("el Lago", "lago.png"),
        Escenario("el Pantano", "pantano.png"),
        Escenario("la Piedra Rúnica", "pieda_runica.png") 
    ]

    @staticmethod
    def obtener_escenarios_ronda(cantidad=3):
        """Devuelve N escenarios únicos aleatorios."""
        return random.sample(ScenarioManager._LUGARES_DISPONIBLES, cantidad)