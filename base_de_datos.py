"""
Manejo de la base de datos PostgreSQL (Neon).
Lee la connection string desde el archivo .env o variable de entorno DATABASE_URL.
"""
import os
import psycopg
from psycopg.rows import dict_row
from datetime import date, timedelta
from pathlib import Path

# Intentar cargar .env si existe
env_path = Path(__file__).parent / ".env"
if env_path.exists():
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, _, val = line.partition("=")
                os.environ.setdefault(key.strip(), val.strip())

DATABASE_URL = os.getenv("DATABASE_URL")


def _conexion():
    if not DATABASE_URL:
        raise RuntimeError(
            "\n\n  ❌ Falta DATABASE_URL.\n"
            "  Creá un archivo .env en esta carpeta con el contenido:\n"
            "  DATABASE_URL=postgresql://usuario:password@host/db?sslmode=require\n"
        )
    return psycopg.connect(DATABASE_URL, row_factory=dict_row)


def init_db():
    """Crea las tablas si no existen."""
    with _conexion() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS pacientes (
                    id              SERIAL PRIMARY KEY,
                    nombre          TEXT NOT NULL,
                    apellido        TEXT NOT NULL,
                    telefono        TEXT NOT NULL,
                    fecha_carga     DATE NOT NULL DEFAULT CURRENT_DATE,
                    mensaje_enviado BOOLEAN NOT NULL DEFAULT FALSE,
                    fecha_envio     TIMESTAMPTZ
                );
            """)
            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_pacientes_pendientes
                ON pacientes (mensaje_enviado, fecha_carga);
            """)
        conn.commit()


def agregar_paciente(nombre: str, apellido: str, telefono: str) -> int:
    with _conexion() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO pacientes (nombre, apellido, telefono)
                VALUES (%s, %s, %s) RETURNING id;
                """,
                (nombre.strip(), apellido.strip(), telefono.strip())
            )
            row = cur.fetchone()
        conn.commit()
        return row["id"]


def pacientes_pendientes_de_ayer() -> list:
    ayer = (date.today() - timedelta(days=1)).isoformat()
    with _conexion() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, nombre, apellido, telefono
                FROM pacientes
                WHERE fecha_carga = %s AND mensaje_enviado = FALSE
                ORDER BY id ASC;
                """,
                (ayer,)
            )
            return cur.fetchall()


def pacientes_pendientes_todos() -> list:
    """
    SOLO PARA PRUEBAS. A diferencia de pacientes_pendientes_de_ayer(),
    esta función ignora la fecha de carga y devuelve TODOS los pacientes
    que todavía no recibieron el mensaje, sin importar cuándo se cargaron.
    No se usa en el envío automático de producción (enviar_encuestas.py),
    solo la usa probar_envio_test.py para poder probar el envío el mismo
    día en que se carga el paciente.
    """
    with _conexion() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, nombre, apellido, telefono
                FROM pacientes
                WHERE mensaje_enviado = FALSE
                ORDER BY id DESC;
                """
            )
            return cur.fetchall()


def marcar_enviado(paciente_id: int):
    with _conexion() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE pacientes
                SET mensaje_enviado = TRUE, fecha_envio = now()
                WHERE id = %s;
                """,
                (paciente_id,)
            )
        conn.commit()


def listar_todos() -> list:
    with _conexion() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT * FROM pacientes ORDER BY fecha_carga DESC, id DESC;"
            )
            rows = cur.fetchall()
    for r in rows:
        if r.get("fecha_carga"):
            r["fecha_carga"] = r["fecha_carga"].isoformat()
        if r.get("fecha_envio"):
            r["fecha_envio"] = r["fecha_envio"].isoformat()
    return rows


# Inicializar al importar
init_db()