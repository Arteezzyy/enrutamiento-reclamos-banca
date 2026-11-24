"""
Modulo de optimizacion para la asignacion de reclamos a areas operativas.

Usa Programacion Lineal Entera (PuLP + CBC) para minimizar una funcion de
costo que combina:

1. La probabilidad que el modelo ML asigna a cada area (fidelidad al modelo).
2. El costo base de cada area (eficiencia operativa).
3. Una penalizacion por desviar el reclamo de su area predicha, que depende
   de la prioridad (los reclamos de prioridad Alta son mas caros de desviar).

Ademas aplica restricciones de capacidad por area y valida la factibilidad
del problema antes de devolver una solucion.
"""

import unicodedata
from collections import Counter

import pulp

PRIORIDADES_VALIDAS = ("Alta", "Media", "Baja")


class ErrorOptimizacion(Exception):
    """Error base del modulo de optimizacion."""


class CapacidadInsuficienteError(ErrorOptimizacion):
    """La demanda supera la capacidad total disponible por turno."""

    def __init__(self, demanda, capacidad_total):
        self.demanda = demanda
        self.capacidad_total = capacidad_total
        super().__init__(
            f"Capacidad insuficiente: hay {demanda} reclamos y la capacidad total "
            f"es de {capacidad_total} por turno."
        )


class OptimizacionInfactibleError(ErrorOptimizacion):
    """El solver no encontro una solucion optima para el modelo planteado."""

    def __init__(self, estado, detalle=""):
        self.estado = estado
        mensaje = f"El solver no encontro una solucion optima (estado: {estado})."
        if detalle:
            mensaje = f"{mensaje} {detalle}"
        super().__init__(mensaje)


def _sin_acentos(valor):
    texto = str(valor or "").lower()
    return "".join(c for c in unicodedata.normalize("NFD", texto) if unicodedata.category(c) != "Mn")


def area_canonica(nombre):
    """Normaliza variantes con o sin tildes a las claves internas del sistema."""
    clave = _sin_acentos(nombre)
    if "soporte" in clave:
        return "Soporte Tecnico"
    if "gerencia" in clave or "riesgo" in clave:
        return "Gerencia de Operaciones/Riesgo"
    if "atencion" in clave or "cliente" in clave:
        return "Atencion al Cliente"
    return str(nombre or "").strip()


def prioridad_canonica(nombre):
    clave = _sin_acentos(nombre)
    for prioridad in PRIORIDADES_VALIDAS:
        if _sin_acentos(prioridad) == clave:
            return prioridad
    return "Media"


class OptimizadorEnrutamiento:
    """Asigna reclamos a areas con programacion lineal entera."""

    # Parametros de la funcion objetivo (documentados y ajustables).
    ALPHA_MODELO = 1.0  # peso de (1 - probabilidad del area)
    BETA_COSTO_BASE = 0.1  # peso del costo base operativo
    GAMMA_DESVIO = {"Alta": 0.6, "Media": 0.3, "Baja": 0.1}  # costo de desviar

    def __init__(self, capacidades=None, slas=None):
        self.capacidades = capacidades or {
            "Soporte Tecnico": 50,
            "Gerencia de Operaciones/Riesgo": 30,
            "Atencion al Cliente": 40,
        }

        self.slas = slas or {
            "Alta": 2,
            "Media": 8,
            "Baja": 24,
        }

        self.penalizacion_sla = {
            "Alta": 100,
            "Media": 50,
            "Baja": 10,
        }

        self.costos_area = {
            "Soporte Tecnico": 1,
            "Gerencia de Operaciones/Riesgo": 2,
            "Atencion al Cliente": 1,
        }

        self.ultimo_resumen = None

    # ------------------------------------------------------------------
    # Utilidades internas
    # ------------------------------------------------------------------

    @staticmethod
    def _variable_binaria(nombre):
        """Crea una variable binaria con la API de PuLP 2.x/3.x.

        PuLP 4.x elimino ``LpVariable(...)`` (las variables se crean desde el
        problema con ``prob.add_variable``), por eso requirements.txt fija
        ``pulp==2.7.0``. Si aun asi se ejecuta con PuLP 4.x, se lanza un error
        claro en lugar de relajar el modelo a variables continuas.
        """
        try:
            return pulp.LpVariable(nombre, cat="Binary")
        except TypeError as exc:
            raise RuntimeError(
                "La version instalada de PuLP no soporta LpVariable(cat=...). "
                f"Se requiere pulp==2.7.0 (instalada: {getattr(pulp, '__version__', '?')})."
            ) from exc

    @staticmethod
    def _probabilidades(reclamo):
        """Devuelve un vector de probabilidades normalizado por area."""
        crudas = reclamo.get("probabilidades_area") or {}
        vector = {}
        for area, valor in crudas.items():
            try:
                vector[area_canonica(area)] = max(0.0, float(valor))
            except (TypeError, ValueError):
                continue

        if not vector:
            predicha = area_canonica(reclamo.get("area_predicha"))
            confianza = reclamo.get("probabilidad_area", 0.5)
            try:
                confianza = min(1.0, max(0.0, float(confianza)))
            except (TypeError, ValueError):
                confianza = 0.5
            vector[predicha] = confianza

        total = sum(vector.values())
        if total <= 0:
            predicha = area_canonica(reclamo.get("area_predicha"))
            return {area: (1.0 if area == predicha else 0.0) for area in vector} or {predicha: 1.0}

        return {area: valor / total for area, valor in vector.items()}

    def _costo_asignacion(self, reclamo, area, probabilidades):
        predicha = area_canonica(reclamo.get("area_predicha"))
        prioridad = prioridad_canonica(reclamo.get("prioridad"))

        probabilidad_area = float(probabilidades.get(area, 0.0))
        coincide = 1.0 if area == predicha else 0.0

        costo_modelo = self.ALPHA_MODELO * (1.0 - probabilidad_area)
        costo_base = self.BETA_COSTO_BASE * self.costos_area.get(area, 1)
        costo_desvio = self.GAMMA_DESVIO.get(prioridad, 0.3) * (1.0 - coincide)

        return costo_modelo + costo_base + costo_desvio

    # ------------------------------------------------------------------
    # Resolucion
    # ------------------------------------------------------------------

    def resolver(self, reclamos, carga_actual=None):
        """
        Resuelve la asignacion optima y devuelve un diccionario con la
        solucion y su resumen. Lanza excepciones si el problema no es factible.
        """
        if not reclamos:
            self.ultimo_resumen = {
                "estado": "vacio",
                "objetivo": 0.0,
                "demanda": 0,
                "capacidad_total": 0,
                "uso_por_area": {area: 0 for area in self.capacidades},
                "asignaciones": [],
            }
            return self.ultimo_resumen

        areas = list(self.capacidades.keys())
        carga = self._carga_actual(reclamos, carga_actual)

        capacidad_disponible = {
            area: max(0, self.capacidades[area] - carga.get(area, 0)) for area in areas
        }
        capacidad_total = sum(capacidad_disponible.values())
        demanda = len(reclamos)

        if demanda > capacidad_total:
            raise CapacidadInsuficienteError(demanda, capacidad_total)

        probabilidades_por_reclamo = [self._probabilidades(reclamo) for reclamo in reclamos]

        problema = pulp.LpProblem("Enrutamiento_Reclamos", pulp.LpMinimize)
        variables = {
            (i, j): self._variable_binaria(f"x_{i}_{j}")
            for i in range(demanda)
            for j in range(len(areas))
        }

        objetivo = []
        for i, reclamo in enumerate(reclamos):
            for j, area in enumerate(areas):
                costo = self._costo_asignacion(reclamo, area, probabilidades_por_reclamo[i])
                objetivo.append(costo * variables[i, j])
        problema += pulp.lpSum(objetivo)

        # Restriccion 1: cada reclamo se asigna a exactamente un area.
        for i in range(demanda):
            problema += pulp.lpSum(variables[i, j] for j in range(len(areas))) == 1

        # Restriccion 2: capacidad maxima por area.
        for j, area in enumerate(areas):
            problema += (
                pulp.lpSum(variables[i, j] for i in range(demanda)) <= capacidad_disponible[area]
            )

        estado_codigo = problema.solve(pulp.PULP_CBC_CMD(msg=0))
        estado = pulp.LpStatus.get(estado_codigo, "Desconocido")

        if estado != "Optimal":
            self.ultimo_resumen = {
                "estado": estado,
                "objetivo": None,
                "demanda": demanda,
                "capacidad_total": capacidad_total,
                "uso_por_area": {},
                "asignaciones": [],
            }
            raise OptimizacionInfactibleError(estado)

        asignaciones = []
        for i, reclamo in enumerate(reclamos):
            for j, area in enumerate(areas):
                if pulp.value(variables[i, j]) is None:
                    continue
                if pulp.value(variables[i, j]) > 0.5:
                    prioridad = prioridad_canonica(reclamo.get("prioridad"))
                    probabilidades = probabilidades_por_reclamo[i]
                    asignaciones.append(
                        {
                            "id": str(reclamo.get("id", i)),
                            "texto": reclamo.get("texto", ""),
                            "area_asignada": area,
                            "area_predicha": area_canonica(reclamo.get("area_predicha")),
                            "prioridad": prioridad,
                            "probabilidad_confianza": round(probabilidades.get(area, 0.0), 4),
                            "probabilidad_predicha": round(
                                probabilidades.get(
                                    area_canonica(reclamo.get("area_predicha")), 0.0
                                ),
                                4,
                            ),
                            "sla_horas": self.slas.get(prioridad, 8),
                            "costo_asignacion": round(
                                self._costo_asignacion(reclamo, area, probabilidades), 4
                            ),
                        }
                    )
                    break

        # Validacion posterior: la solucion debe cumplir todas las restricciones.
        uso_por_area = Counter(asignacion["area_asignada"] for asignacion in asignaciones)
        self._validar_solucion(asignaciones, uso_por_area, capacidad_disponible, demanda)

        self.ultimo_resumen = {
            "estado": "optimo",
            "objetivo": round(float(pulp.value(problema.objective) or 0.0), 4),
            "demanda": demanda,
            "capacidad_total": capacidad_total,
            "uso_por_area": {area: int(uso_por_area.get(area, 0)) for area in areas},
            "asignaciones": asignaciones,
        }
        return self.ultimo_resumen

    def asignar_optimo(self, reclamos, carga_actual=None):
        """Compatibilidad: devuelve solo la lista de asignaciones."""
        return self.resolver(reclamos, carga_actual=carga_actual)["asignaciones"]

    def _carga_actual(self, reclamos, carga_actual):
        if carga_actual:
            return {area_canonica(area): int(valor) for area, valor in carga_actual.items()}
        if reclamos:
            heredada = reclamos[0].get("carga_actual_area") or {}
            return {area_canonica(area): int(valor) for area, valor in heredada.items()}
        return {}

    @staticmethod
    def _validar_solucion(asignaciones, uso_por_area, capacidad_disponible, demanda):
        if len(asignaciones) != demanda:
            raise OptimizacionInfactibleError(
                "Solucion incompleta",
                f"Se asignaron {len(asignaciones)} de {demanda} reclamos.",
            )

        for area, cantidad in uso_por_area.items():
            if cantidad > capacidad_disponible.get(area, 0):
                raise OptimizacionInfactibleError(
                    "Capacidad excedida",
                    f"El area {area} recibio {cantidad} reclamos y solo admite "
                    f"{capacidad_disponible.get(area, 0)}.",
                )

    # ------------------------------------------------------------------
    # Parametros de negocio
    # ------------------------------------------------------------------

    def obtener_capacidades(self):
        return self.capacidades

    def obtener_slas(self):
        return self.slas

    def obtener_parametros(self):
        return {
            "alpha_modelo": self.ALPHA_MODELO,
            "beta_costo_base": self.BETA_COSTO_BASE,
            "gamma_desvio": self.GAMMA_DESVIO,
            "costos_base": self.costos_area,
            "penalizacion_sla": self.penalizacion_sla,
        }
