"""
Modulo de Optimización para asignación eficiente de reclamos.
Utiliza Programación Lineal Entera (PuLP) para asignar reclamos a áreas
considerando probabilidades del modelo ML, capacidades máximas por área,
SLAs de respuesta y carga de trabajo en tiempo real.
"""

import pulp


class OptimizadorEnrutamiento:
    def __init__(self):
        # Capacidades máximas de atención por área (reclamos por turno)
        self.capacidades = {
            "Soporte Tecnico": 50,
            "Gerencia de Operaciones/Riesgo": 30,
            "Atencion al Cliente": 40,
        }

        # SLA (horas máximas de respuesta por prioridad)
        self.slas = {
            "Alta": 2,
            "Media": 8,
            "Baja": 24,
        }

        # Penalización por incumplimiento de SLA (costo por hora de retraso)
        self.penalizacion_sla = {
            "Alta": 100,
            "Media": 50,
            "Baja": 10,
        }

        # Costo base de asignación por área (menor = más eficiente)
        self.costos_area = {
            "Soporte Tecnico": 1,
            "Gerencia de Operaciones/Riesgo": 2,
            "Atencion al Cliente": 1,
        }

    def asignar_optimo(self, reclamos):
        """
        Asigna cada reclamo a un área de forma óptima.

        Parametros:
        - reclamos: lista de diccionarios con llaves:
            id, texto, area_predicha, prioridad, probabilidad_area (float 0-1),
            carga_actual_area (opcional, dict area -> carga actual)

        Retorna:
        - lista de asignaciones: [{id, area_asignada, prioridad, costo}]
        """
        if not reclamos:
            return []

        areas = list(self.capacidades.keys())
        n_reclamos = len(reclamos)

        # Problema de optimización
        prob = pulp.LpProblem("Enrutamiento_Reclamos", pulp.LpMinimize)

        # Variables de decisión: x[i][j] = 1 si reclamo i se asigna a area j
        x = {}
        for i in range(n_reclamos):
            for j, area in enumerate(areas):
                x[i, j] = pulp.LpVariable(f"x_{i}_{j}", cat="Binary")

        # Función objetivo: minimizar costo total
        # Costo = costo_base_area * (1 - probabilidad_confianza) + penalizacion_sla
        funcion_objetivo = []
        for i, reclamo in enumerate(reclamos):
            prioridad = reclamo.get("prioridad", "Media")
            prob_confianza = reclamo.get("probabilidad_area", 0.5)
            penalizacion = self.penalizacion_sla.get(prioridad, 50)

            for j, area in enumerate(areas):
                # Si el área asignada coincide con la predicción ML, costo menor
                coincide = 1 if area == reclamo.get("area_predicha") else 0
                costo = (
                    self.costos_area.get(area, 1) * (1 - 0.5 * coincide)
                    + penalizacion * (1 - prob_confianza)
                )
                funcion_objetivo.append(costo * x[i, j])

        prob += pulp.lpSum(funcion_objetivo)

        # Restricción 1: cada reclamo se asigna a exactamente una área
        for i in range(n_reclamos):
            prob += pulp.lpSum([x[i, j] for j in range(len(areas))]) == 1

        # Restricción 2: capacidad máxima por área
        for j, area in enumerate(areas):
            carga_actual = reclamos[0].get("carga_actual_area", {}).get(area, 0) if reclamos else 0
            prob += pulp.lpSum([x[i, j] for i in range(n_reclamos)]) <= self.capacidades[area] - carga_actual

        # Resolver
        prob.solve(pulp.PULP_CBC_CMD(msg=0))

        # Extraer resultados
        asignaciones = []
        for i, reclamo in enumerate(reclamos):
            for j, area in enumerate(areas):
                if pulp.value(x[i, j]) == 1:
                    asignaciones.append({
                        "id": reclamo.get("id", i),
                        "texto": reclamo.get("texto", ""),
                        "area_asignada": area,
                        "area_predicha": reclamo.get("area_predicha", ""),
                        "prioridad": reclamo.get("prioridad", "Media"),
                        "probabilidad_confianza": reclamo.get("probabilidad_area", 0.0),
                        "sla_horas": self.slas.get(reclamo.get("prioridad", "Media"), 8),
                    })
                    break

        return asignaciones

    def obtener_capacidades(self):
        return self.capacidades

    def obtener_slas(self):
        return self.slas