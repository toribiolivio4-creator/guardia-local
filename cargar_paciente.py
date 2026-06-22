"""
cargar_paciente.py
──────────────────
Script para que el personal de la guardia cargue el nombre, apellido
y teléfono de un paciente. Al día siguiente a las 9hs recibirá por
WhatsApp el link al formulario de satisfacción.

Uso:
    python cargar_paciente.py
"""
import sys
import re
from base_de_datos import agregar_paciente, listar_todos
from datetime import date, timedelta


VERDE   = "\033[92m"
AMARILLO = "\033[93m"
ROJO    = "\033[91m"
AZUL    = "\033[94m"
NEGRITA = "\033[1m"
RESET   = "\033[0m"


def limpiar_pantalla():
    import os
    os.system("cls" if os.name == "nt" else "clear")


def titulo():
    print(f"{AZUL}{NEGRITA}")
    print("╔══════════════════════════════════════════╗")
    print("║     GUARDIA MÉDICA · Carga de Paciente   ║")
    print("╚══════════════════════════════════════════╝")
    print(RESET)


def pedir_campo(nombre_campo: str, opcional: bool = False) -> str:
    while True:
        valor = input(f"  {nombre_campo}: ").strip()
        if valor:
            return valor
        if opcional:
            return ""
        print(f"  {ROJO}⚠  Este campo es obligatorio.{RESET}")


def validar_telefono(tel: str) -> str:
    """Limpia el teléfono y lo normaliza (solo dígitos, puede tener + al inicio)."""
    # Eliminar espacios, guiones, paréntesis
    limpio = re.sub(r"[\s\-\(\)\.]+", "", tel)
    # Verificar que tenga al menos 8 dígitos
    digitos = re.sub(r"[^\d]", "", limpio)
    if len(digitos) < 8:
        return ""
    return limpio


def mostrar_tabla_pacientes():
    """Muestra los últimos pacientes cargados de forma prolija."""
    pacientes = listar_todos()
    if not pacientes:
        print(f"  {AMARILLO}Todavía no hay pacientes cargados.{RESET}\n")
        return

    hoy = date.today().isoformat()
    ayer = (date.today() - timedelta(days=1)).isoformat()

    print(f"\n  {NEGRITA}{'ID':<5} {'Nombre':<20} {'Teléfono':<18} {'Fecha':<12} {'Estado'}{RESET}")
    print("  " + "─" * 72)

    for p in pacientes[:20]:
        estado = f"{VERDE}✓ Enviado{RESET}" if p["mensaje_enviado"] else f"{AMARILLO}⏳ Pendiente{RESET}"
        fecha = p["fecha_carga"]
        if fecha == hoy:
            fecha_txt = f"{AZUL}Hoy{RESET}      "
        elif fecha == ayer:
            fecha_txt = f"{AMARILLO}Ayer{RESET}     "
        else:
            fecha_txt = fecha

        nombre_completo = f"{p['nombre']} {p['apellido']}"[:20]
        print(f"  {p['id']:<5} {nombre_completo:<20} {p['telefono']:<18} {fecha_txt:<12} {estado}")

    if len(pacientes) > 20:
        print(f"  {AMARILLO}... y {len(pacientes) - 20} más.{RESET}")
    print()


def cargar_nuevo_paciente():
    print(f"\n  {NEGRITA}── Datos del paciente ─────────────────────{RESET}\n")

    nombre = pedir_campo("Nombre")
    apellido = pedir_campo("Apellido")

    while True:
        tel_raw = pedir_campo("Teléfono celular (ej: 11 2345-6789)")
        tel = validar_telefono(tel_raw)
        if tel:
            break
        print(f"  {ROJO}⚠  Teléfono inválido. Ingresá al menos 8 dígitos.{RESET}")

    print(f"\n  Confirmá los datos:")
    print(f"    Nombre:    {NEGRITA}{nombre} {apellido}{RESET}")
    print(f"    Teléfono:  {NEGRITA}{tel}{RESET}")
    print(f"    Mensaje:   Se enviará mañana a las 9:00 hs\n")

    while True:
        confirmar = input("  ¿Guardás? (s/n): ").strip().lower()
        if confirmar in ("s", "si", "sí", "y", "yes"):
            nuevo_id = agregar_paciente(nombre, apellido, tel)
            print(f"\n  {VERDE}{NEGRITA}✓ Paciente guardado correctamente (ID #{nuevo_id}).{RESET}")
            print(f"  {VERDE}  Recibirá el WhatsApp mañana a las 9:00 hs.{RESET}\n")
            return
        elif confirmar in ("n", "no"):
            print(f"\n  {AMARILLO}Cancelado. No se guardó nada.{RESET}\n")
            return
        else:
            print(f"  Escribí 's' para confirmar o 'n' para cancelar.")


def menu():
    limpiar_pantalla()
    titulo()

    while True:
        print(f"  {NEGRITA}¿Qué querés hacer?{RESET}\n")
        print("    [1] Cargar nuevo paciente")
        print("    [2] Ver pacientes cargados")
        print("    [3] Salir\n")

        opcion = input("  Opción: ").strip()

        if opcion == "1":
            cargar_nuevo_paciente()
        elif opcion == "2":
            print()
            mostrar_tabla_pacientes()
        elif opcion == "3":
            print(f"\n  {AZUL}Hasta luego.{RESET}\n")
            sys.exit(0)
        else:
            print(f"  {ROJO}Opción no válida. Escribí 1, 2 o 3.{RESET}\n")


if __name__ == "__main__":
    menu()
