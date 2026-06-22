"""
enviar_encuestas.py
───────────────────
Tarea que corre todos los días a las 9:00 hs.
Lee la base de datos, busca los pacientes cargados ayer que no
recibieron mensaje, y les manda el WhatsApp con el link a la encuesta.

Modos de uso:

  1) Modo cron (queda corriendo en segundo plano, envía a las 9hs):
        python enviar_encuestas.py

  2) Envío inmediato de prueba:
        python enviar_encuestas.py --ahora

IMPORTANTE:
  - La PC tiene que estar encendida y con sesión de WhatsApp Web iniciada.
  - Chrome tiene que estar instalado como navegador.
  - No toques la PC mientras manda los mensajes (PyWhatKit toma el control
    del navegador por unos segundos por cada mensaje).
"""
import sys
import time
import pywhatkit
import schedule
from datetime import datetime

from base_de_datos import pacientes_pendientes_de_ayer, marcar_enviado

LINK_ENCUESTA = "https://encuesta-guardia.vercel.app/"

VERDE    = "\033[92m"
AMARILLO = "\033[93m"
ROJO     = "\033[91m"
AZUL     = "\033[94m"
NEGRITA  = "\033[1m"
RESET    = "\033[0m"


def normalizar_telefono(tel: str) -> str:
    """
    Convierte el teléfono al formato que espera PyWhatKit: +549XXXXXXXXXX
    Ejemplos:
      '11 2345-6789'  → '+5491123456789'
      '1123456789'    → '+5491123456789'
      '+5491123456789'→ '+5491123456789'  (ya está bien)
    """
    import re
    limpio = re.sub(r"[\s\-\(\)\.]+", "", tel)
    digitos = re.sub(r"[^\d]", "", limpio)

    if limpio.startswith("+"):
        return limpio          # ya tiene código de país

    if digitos.startswith("549"):
        return "+" + digitos
    if digitos.startswith("54"):
        return "+" + digitos
    if digitos.startswith("0"):
        digitos = digitos[1:]  # quitar el 0 de discado largo
    # Asumir Argentina: +549 + número sin 15
    if digitos.startswith("15"):
        digitos = digitos[2:]
    return "+549" + digitos


def armar_mensaje(nombre: str) -> str:
    return (
        f"Hola {nombre} 👋, esperamos que te encuentres mejor.\n\n"
        f"Nos gustaría conocer tu opinión sobre la atención que recibiste "
        f"en la guardia. ¿Podrías completar esta breve encuesta?\n\n"
        f"👉 {LINK_ENCUESTA}\n\n"
        f"¡Muchas gracias! Tu opinión nos ayuda a mejorar 🙏"
    )


def enviar_a_todos():
    ahora = datetime.now().strftime("%H:%M:%S")
    print(f"\n{AZUL}{NEGRITA}[{ahora}] Iniciando envío de encuestas...{RESET}")

    pendientes = pacientes_pendientes_de_ayer()

    if not pendientes:
        print(f"  {AMARILLO}No hay pacientes pendientes de ayer.{RESET}")
        return

    print(f"  {NEGRITA}Pacientes a contactar: {len(pendientes)}{RESET}\n")

    for p in pendientes:
        nombre    = p["nombre"]
        apellido  = p["apellido"]
        telefono  = normalizar_telefono(p["telefono"])
        mensaje   = armar_mensaje(nombre)

        print(f"  → Enviando a {nombre} {apellido} ({telefono})... ", end="", flush=True)

        try:
            # wait_time=15: espera 15 segundos después de abrir WhatsApp Web
            # antes de mandar el mensaje (da tiempo a que cargue)
            # tab_close=True: cierra la pestaña después de enviar
            pywhatkit.sendwhatmsg(
                phone_no=telefono,
                message=mensaje,
                time_hour=datetime.now().hour,
                time_min=datetime.now().minute + 1,  # 1 minuto en el futuro
                wait_time=15,
                tab_close=True,
                close_time=5,
            )
            marcar_enviado(p["id"])
            print(f"{VERDE}✓ Enviado{RESET}")
        except Exception as e:
            print(f"{ROJO}✗ Error: {e}{RESET}")

        # Esperar entre mensajes para no abrir 10 pestañas al mismo tiempo
        time.sleep(20)

    print(f"\n{VERDE}{NEGRITA}Envíos completados.{RESET}\n")


def main():
    modo_ahora = "--ahora" in sys.argv

    if modo_ahora:
        # Envío inmediato (para probar)
        print(f"{AZUL}{NEGRITA}── Modo prueba: envío inmediato ──{RESET}")
        enviar_a_todos()
        return

    # Modo cron: queda corriendo y envía a las 9:00 hs todos los días
    print(f"\n{AZUL}{NEGRITA}╔══════════════════════════════════════════╗")
    print(        "║   GUARDIA MÉDICA · Envío automático WA   ║")
    print(        "╚══════════════════════════════════════════╝{RESET}")
    print(f"\n  Cron iniciado. Se enviarán los mensajes todos los días a las {NEGRITA}09:00 hs{RESET}.")
    print(f"  {AMARILLO}No cierres esta ventana.{RESET}")
    print(f"  Presioná Ctrl+C para detener.\n")

    schedule.every().day.at("09:00").do(enviar_a_todos)

    # Mostrar próxima ejecución
    prox = schedule.next_run()
    print(f"  Próximo envío: {NEGRITA}{prox.strftime('%d/%m/%Y %H:%M')}{RESET}\n")

    while True:
        schedule.run_pending()
        time.sleep(30)  # revisar cada 30 segundos


if __name__ == "__main__":
    main()
