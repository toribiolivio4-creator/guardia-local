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

    print(f"\n  {NEGRITA}{'ID':<5} {'DNI':<12} {'Nombre':<20} {'Teléfono':<18} {'Fecha':<12} {'Estado'}{RESET}")
    print("  " + "─" * 85)

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
        dni = p.get("dni", "") or ""
        print(f"  {p['id']:<5} {dni:<12} {nombre_completo:<20} {p['telefono']:<18} {fecha_txt:<12} {estado}")

    if len(pacientes) > 20:
        print(f"  {AMARILLO}... y {len(pacientes) - 20} más.{RESET}")
    print()


def buscar_y_mostrar_paciente():
    dni = pedir_campo("DNI del paciente")
    from base_de_datos import buscar_por_dni
    paciente = buscar_por_dni(dni)
    if paciente:
        print(f"\n  {VERDE}✓ Paciente encontrado:{RESET}")
        print(f"    {NEGRITA}{paciente['nombre']} {paciente['apellido']}{RESET}")
        print(f"    Teléfono: {paciente['telefono']}")
        if paciente["mensaje_enviado"]:
            print(f"    Estado: {AMARILLO}Ya fue enviado{RESET}")
        else:
            print(f"    Estado: {VERDE}Pendiente de envío{RESET}")
        print()
        while True:
            r = input("  ¿Querés reactivarlo para que reciba el WhatsApp mañana? (s/n): ").strip().lower()
            if r in ("s", "si", "sí", "y", "yes"):
                tel_raw = input(f"  Teléfono (actual: {paciente['telefono']}, Enter para mantener): ").strip()
                if tel_raw:
                    tel = validar_telefono(tel_raw)
                    if tel:
                        from base_de_datos import actualizar_telefono
                        actualizar_telefono(paciente["id"], tel)
                    else:
                        print(f"  {ROJO}Teléfono inválido, se mantiene el actual.{RESET}")
                from base_de_datos import reactivar_paciente
                reactivar_paciente(paciente["id"])
                print(f"\n  {VERDE}{NEGRITA}✓ {paciente['nombre']} {paciente['apellido']} reactivado. Recibirá WhatsApp mañana a las 9:00 hs.{RESET}\n")
                return
            elif r in ("n", "no"):
                print(f"  {AMARILLO}No se realizaron cambios.{RESET}\n")
                return
    else:
        print(f"  {AMARILLO}Paciente no encontrado. Cargá los datos como nuevo.{RESET}\n")
        cargar_nuevo_paciente_con_dni(dni)


def cargar_nuevo_paciente_con_dni(dni=""):
    print(f"\n  {NEGRITA}── Datos del paciente ─────────────────────{RESET}\n")

    if not dni:
        dni = pedir_campo("DNI")
    nombre = pedir_campo("Nombre")
    apellido = pedir_campo("Apellido")

    while True:
        tel_raw = pedir_campo("Teléfono celular (ej: 11 2345-6789)")
        tel = validar_telefono(tel_raw)
        if tel:
            break
        print(f"  {ROJO}⚠  Teléfono inválido. Ingresá al menos 8 dígitos.{RESET}")

    print(f"\n  Confirmá los datos:")
    print(f"    DNI:       {NEGRITA}{dni}{RESET}")
    print(f"    Nombre:    {NEGRITA}{nombre} {apellido}{RESET}")
    print(f"    Teléfono:  {NEGRITA}{tel}{RESET}")
    print(f"    Mensaje:   Se enviará mañana a las 9:00 hs\n")

    while True:
        confirmar = input("  ¿Guardás? (s/n): ").strip().lower()
        if confirmar in ("s", "si", "sí", "y", "yes"):
            nuevo_id = agregar_paciente(nombre, apellido, tel, dni)
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
        print("    [1] Buscar paciente por DNI (reactivar si ya existe)")
        print("    [2] Cargar paciente nuevo")
        print("    [3] Ver pacientes cargados")
        print("    [4] Salir\n")

        opcion = input("  Opción: ").strip()

        if opcion == "1":
            buscar_y_mostrar_paciente()
        elif opcion == "2":
            cargar_nuevo_paciente_con_dni()
        elif opcion == "3":
            print()
            mostrar_tabla_pacientes()
        elif opcion == "4":
            print(f"\n  {AZUL}Hasta luego.{RESET}\n")
            sys.exit(0)
        else:
            print(f"  {ROJO}Opción no válida. Escribí 1, 2, 3 o 4.{RESET}\n")


if __name__ == "__main__":
    menu()
