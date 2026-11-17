"""
Persistencia simple de reclamos en SQLite.

Se usa una base local (`datos/reclamos.db`) para que el historial sobreviva a
los reinicios de la API sin necesidad de un motor de base de datos externo.
"""

import json
import os
import sqlite3
import threading

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATOS_DIR = os.path.join(BASE_DIR, "datos")
DB_PATH = os.path.join(DATOS_DIR, "reclamos.db")

_lock = threading.Lock()


def _conectar():
    conexion = sqlite3.connect(DB_PATH, timeout=10)
    conexion.row_factory = sqlite3.Row
    return conexion


def inicializar():
    os.makedirs(DATOS_DIR, exist_ok=True)
    with _conectar() as conexion:
        conexion.execute("PRAGMA journal_mode=WAL")
        conexion.execute(
            """
            CREATE TABLE IF NOT EXISTS reclamos (
                id TEXT PRIMARY KEY,
                texto TEXT NOT NULL,
                area TEXT NOT NULL,
                prioridad TEXT NOT NULL,
                fecha TEXT NOT NULL,
                probabilidades_area TEXT,
                probabilidades_prioridad TEXT
            )
            """
        )
        conexion.execute(
            "CREATE INDEX IF NOT EXISTS idx_reclamos_fecha ON reclamos (fecha DESC)"
        )
        conexion.commit()


def _serializar(registro):
    return (
        registro["id"],
        registro["texto"],
        registro["area"],
        registro["prioridad"],
        registro["fecha"],
        json.dumps(registro.get("probabilidades_area") or {}, ensure_ascii=False),
        json.dumps(registro.get("probabilidades_prioridad") or {}, ensure_ascii=False),
    )


def _deserializar(fila):
    return {
        "id": fila["id"],
        "texto": fila["texto"],
        "area": fila["area"],
        "prioridad": fila["prioridad"],
        "fecha": fila["fecha"],
        "probabilidades_area": json.loads(fila["probabilidades_area"] or "{}"),
        "probabilidades_prioridad": json.loads(fila["probabilidades_prioridad"] or "{}"),
    }


def insertar(registro):
    with _lock, _conectar() as conexion:
        conexion.execute(
            """
            INSERT OR REPLACE INTO reclamos
                (id, texto, area, prioridad, fecha, probabilidades_area, probabilidades_prioridad)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            _serializar(registro),
        )
        conexion.commit()
    return registro


def listar(limite=None):
    with _conectar() as conexion:
        sql = "SELECT * FROM reclamos ORDER BY fecha DESC, id DESC"
        parametros = ()
        if limite:
            sql += " LIMIT ?"
            parametros = (int(limite),)
        filas = conexion.execute(sql, parametros).fetchall()
    return [_deserializar(fila) for fila in filas]


def obtener(reclamo_id):
    with _conectar() as conexion:
        fila = conexion.execute(
            "SELECT * FROM reclamos WHERE id = ?", (reclamo_id,)
        ).fetchone()
    return _deserializar(fila) if fila else None


def contar():
    with _conectar() as conexion:
        return int(conexion.execute("SELECT COUNT(*) FROM reclamos").fetchone()[0])


def limpiar():
    """Utilidad para pruebas: elimina todos los reclamos registrados."""
    with _lock, _conectar() as conexion:
        conexion.execute("DELETE FROM reclamos")
        conexion.commit()
