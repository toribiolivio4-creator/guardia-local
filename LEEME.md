# Guardia Médica · Sistema de Encuestas WhatsApp

---

## INSTRUCCIONES DE USO

### PASO 1 — Instalar (una sola vez)

1. Asegurate de tener **Python** instalado → https://www.python.org/downloads/
   (durante la instalación tildá "Add Python to PATH")

2. Abrí una ventana de **Símbolo del sistema** (CMD) en esta carpeta y escribí:
   ```
   pip install -r requirements.txt
   ```

3. Tené **Google Chrome** instalado.

---

### PARA USAR TODOS LOS DÍAS

#### Cargar un paciente (después de cada consulta)
→ Hacé doble click en **CARGAR_PACIENTE.bat**

Ingresás nombre, apellido y teléfono. El paciente recibirá el WhatsApp al día siguiente a las 9hs.

#### Envío automático a las 9hs
→ Hacé doble click en **INICIAR_CRON.bat** (dejalo abierto toda la jornada)

Todos los días a las 9hs, el programa abre WhatsApp Web automáticamente y manda el mensaje a los pacientes cargados el día anterior. **No cierres esa ventana.**

Si la PC se reinicia, acordate de volver a abrir INICIAR_CRON.bat.

---

### PARA PROBAR

→ Hacé doble click en **PROBAR_ENVIO_AHORA.bat**

Esto envía los mensajes en el momento (sin esperar las 9hs). Útil para verificar que todo funciona.

---

### ARCHIVOS IMPORTANTES

| Archivo | Para qué sirve |
|---|---|
| `pacientes.db` | Base de datos local con todos los pacientes |
| `CARGAR_PACIENTE.bat` | Carga un nuevo paciente |
| `INICIAR_CRON.bat` | Envío automático diario |
| `PROBAR_ENVIO_AHORA.bat` | Probar el envío manualmente |

---

### IMPORTANTE — WhatsApp Web

- La PC tiene que estar **encendida y con WhatsApp Web abierto** (web.whatsapp.com) cuando el programa mande los mensajes.
- Si es la primera vez, abrir web.whatsapp.com, escanear el QR con el celular del hospital.
- Mientras el programa manda mensajes, **no toques el mouse ni el teclado**, lo hace solo.

---

### PREGUNTAS FRECUENTES

**¿Dónde se guardan los datos?**
En el archivo `pacientes.db` de esta misma carpeta. Si hacés una copia de esa carpeta tenés un backup.

**¿Qué pasa si un paciente no recibe el mensaje?**
Abrí `PROBAR_ENVIO_AHORA.bat` para reintentar. Si sigue fallando, verificá que el teléfono esté bien escrito.

**¿Puedo ver todos los pacientes cargados?**
Sí, abrí `CARGAR_PACIENTE.bat` y elegí la opción 2.
