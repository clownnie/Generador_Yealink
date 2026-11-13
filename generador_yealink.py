import os
import re
import tkinter as tk
from tkinter import messagebox, filedialog

def limpiar_mac(mac_sucia):
    # Remueve dos puntos, guiones, espacios y lo pasa a minúsculas
    return re.sub(r"[\s:-]", "", mac_sucia).lower()

def generar_config_yealink(sv_ip, mac, extension, secret, pb_url, pb_name, firmware_url, sv_ntp, ltime_zone, a_pass):
# Definimos el nombre de la zona horaria automáticamente según el número ingresado
    if ltime_zone == "-4":
        ltime_name = "Chile(Santiago)"
    elif ltime_zone == "-3":
        ltime_name = "Argentina(Buenos Aires)"

    # Plantilla de configuración adaptada para teléfonos Yealink (.cfg)
    plantilla = f"""#!version:1.0.0.1

# ---------------------------------------------------------------------
# PARÁMETROS DE CUENTA SIP Y LÍNEA 1
# ---------------------------------------------------------------------
# Habilita o deshabilita la línea SIP (1 = Activa, 0 = Inactiva)
account.1.enable = 1

# Etiqueta visible en la pantalla principal junto al botón de línea
account.1.label = {extension}

# Nombre que se muestra en la pantalla física del teléfono durante llamadas
account.1.display_name = {extension}

# Nombre de usuario SIP (User ID) registrado en la PBX
account.1.user_name = {extension}

# Nombre de autenticación SIP (Authenticate ID) en la PBX
account.1.auth_name = {extension}

# Contraseña de la extensión (Secret) configurada en la PBX
account.1.password = {secret}

# Nivel de retorno de voz local/efecto de tono lateral (sidetone)
voice.side_tone = -3

# Dirección IP del servidor SIP primario (PBX)
account.1.sip_server.1.address = {sv_ip}

# ---------------------------------------------------------------------
# SEGURIDAD Y ACCESO DE ADMINISTRADOR
# ---------------------------------------------------------------------
# Define la contraseña de acceso para el usuario administrador del teléfono
security.user_password = admin:{a_pass}

# ---------------------------------------------------------------------
# CONFIGURACIÓN REGIONAL Y HORARIA
# ---------------------------------------------------------------------
# Idioma de la pantalla gráfica del teléfono (GUI)
lang.gui = Spanish_LA

# Idioma de la interfaz web de administración (WUI)
lang.wui = Spanish

# Formato de fecha en pantalla (3 = DD MMM WWW / Ejemplo: 12 Nov Mié)
local_time.date_format = 3

# Servidor NTP primario para sincronización horaria
local_time.ntp_server1 = {sv_ntp}

# Servidor NTP secundario (deshabilitado/vacío)
local_time.ntp_server2 = %EMPTY%

# Zona horaria, -4 para "Chile" en horario de invierno y -3 para horario de verano con "Argentina".
local_time.time_zone = {ltime_zone}

# Nombre de la zona horaria asignada, se asigna un nombre u otro dependiendo del valor de ltime_zone, que es entre -4 y -3... Holis.
local_time.time_zone_name = {ltime_name}

# ---------------------------------------------------------------------
# APROVISIONAMIENTO AUTOMÁTICO POR FTP
# ---------------------------------------------------------------------
# URL del servidor de autoprovisionamiento (TFTP/HTTP/HTTPS/FTP)
# No lo necesita al utilizar HTTP, ya que se lo entrega el option 66 del DHCP. Con FTP es necesario agregarlo.
# static.auto_provision.server.url = ftp://{sv_ip}/provisioning/

# Nombre de usuario si el servidor requiere autenticación FTP/HTTP
static.auto_provision.server.username = 

# Contraseña si el servidor requiere autenticación FTP/HTTP
static.auto_provision.server.password = 

# Protección contra sobreescritura de parámetros modificados localmente (0 = Desactivado)
static.auto_provision.custom.protect = 0

# ---------------------------------------------------------------------
# ACTUALIZACIÓN DE FIRMWARE
# ---------------------------------------------------------------------
# Ruta completa de descarga remota del firmware (.rom) específico para el modelo
static.firmware.url = {firmware_url}

# ---------------------------------------------------------------------
# AGENDA REMOTA / TELEFÓNICA (REMOTE PHONEBOOK)
# ---------------------------------------------------------------------
# Enlace de la agenda remota
remote_phonebook.data.1.url = {pb_url}

# Nombre en que aparece la agenda en el menú de usuario
remote_phonebook.data.1.name = {pb_name}

# Habilita la actualización de la agenda al presionar el menú o entrar en ella
features.remote_phonebook.enter_update_enable = 1

# Tiempo de refresco/actualización periódica de la agenda en segundos (3600s = 1 hora)
features.remote_phonebook.flash_time = 3600

# Habilita la funcionalidad de agenda de direcciones remota
features.remote_phonebook.enable = 1

# Nombre que se mostrará en el menú contextual de directorio
remote_phonebook.display_name = {pb_name}

# Habilita la agenda remota en la configuración de directorios integrados
directory_setting.remote_phone_book.enable = 1

# Prioridad de búsqueda en la agenda de direcciones remota (por defecto)
directory_setting.remote_phone_book.priority = 

# Permite realizar búsquedas automáticas en la agenda remota mientras se marca un número
search_in_dialing.remote_phone_book.enable = 1

# Prioridad de búsqueda en marcado para la agenda remota (por defecto)
search_in_dialing.remote_phone_book.priority = 
"""
    return plantilla

def seleccionar_carpeta(entry_carpeta):
    # Abre una ventana para elegir la carpeta de destino de forma visual
    carpeta_elegida = filedialog.askdirectory(title="Selecciona la carpeta donde guardar los archivos .cfg")
    if carpeta_elegida:
        entry_carpeta.delete(0, tk.END)
        entry_carpeta.insert(0, carpeta_elegida)

def procesar_datos(entry_sv_ip, entry_pb_url, entry_pb_name, entry_firmware_url, entry_sv_ntp, entry_ltime_zone, entry_a_pass, entry_carpeta, text_datos):
    sv_ip = entry_sv_ip.get().strip()
    pb_url = entry_pb_url.get().strip()
    pb_name = entry_pb_name.get().strip()
    firmware_default = entry_firmware_url.get().strip()
    ltime_zone = entry_ltime_zone.get().strip()
    a_pass = entry_a_pass.get().strip()
    sv_ntp = entry_sv_ntp.get().strip()
    
    # Obtener la carpeta elegida por el usuario, o usar la por defecto si está vacía
    carpeta_personalizada = entry_carpeta.get().strip()
    if carpeta_personalizada:
        carpeta_salida = carpeta_personalizada
    else:
        carpeta_salida = os.path.join(os.getcwd(), "archivos_cfg_yealink")

    if not sv_ip:
        messagebox.showerror("Error", "Debes ingresar al menos la IP del Servidor SIP.")
        return

    texto_bruto = text_datos.get("1.0", tk.END).strip()
    if not texto_bruto:
        messagebox.showerror("Error", "La lista está vacía. Pega las filas desde Excel.")
        return

    try:
        os.makedirs(carpeta_salida, exist_ok=True)
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo crear o acceder a la carpeta de salida:\n{e}")
        return

    conteo = 0
    lineas = texto_bruto.split("\n")

    try:
        for linea in lineas:
            linea = linea.strip()
            if not linea:
                continue

            # Separador flexible: detecta tabulaciones (\t), comas (,) o espacios múltiples (\s+)
            partes = [p.strip() for p in re.split(r'[\t,\s]+', linea) if p.strip()]

            # Mínimo 3 columnas obligatorias: MAC, Extensión, Secret
            if len(partes) < 3:
                continue

            mac_limpia = limpiar_mac(partes[0])
            ext = partes[1]
            secret = partes[2]

            if len(mac_limpia) != 12:
                print(f"Advertencia: MAC inválida omitida -> {partes[0]}")
                continue

            # 4ta columna opcional para Firmware personalizado por fila
            if len(partes) >= 4 and partes[3]:
                firmware_url = partes[3]
            else:
                firmware_url = firmware_default

            contenido_cfg = generar_config_yealink(sv_ip, mac_limpia, ext, secret, pb_url, pb_name, firmware_url, sv_ntp, ltime_zone, a_pass)

            # Los teléfonos Yealink leen archivos .cfg nombrados estrictamente con su MAC (sin prefijos)
            nombre_archivo = f"{mac_limpia}.cfg"
            ruta_completa = os.path.join(carpeta_salida, nombre_archivo)

            with open(ruta_completa, mode='w', encoding='utf-8') as cfg_file:
                cfg_file.write(contenido_cfg)

            conteo += 1

        if conteo > 0:
            messagebox.showinfo(
                "¡Éxito!",
                f"Se han generado {conteo} archivos .cfg de Yealink exitosamente.\n\nRevisa la carpeta:\n{carpeta_salida}"
            )
        else:
            messagebox.showwarning(
                "Atención",
                "No se procesó ninguna línea válida. Asegúrate de copiar al menos las columnas: MAC, Extensión y Secret."
            )

    except Exception as e:
        messagebox.showerror("Error", f"Ocurrió un problema al procesar los datos:\n{e}")

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Generador masivo Yealink")
    root.geometry("680x760")
    root.minsize(580, 600)

    label = tk.Label(
        root,
        text="Generador masivo de configuración Yealink",
        font=("Arial", 11, "bold"),
        pady=5
    )
    label.pack()

    # Marco de parámetros generales
    frame_params = tk.LabelFrame(root, text=" Parámetros Generales (Por defecto) ", font=("Arial", 9, "bold"), padx=10, pady=8)
    frame_params.pack(padx=15, pady=5, fill="x")

    tk.Label(frame_params, text="IP Servidor SIP:", anchor="w").grid(row=0, column=0, sticky="w", pady=3)
    entry_sv_ip = tk.Entry(frame_params, width=45)
    entry_sv_ip.grid(row=0, column=1, pady=3, sticky="we", columnspan=2)

    tk.Label(frame_params, text="URL Agenda:", anchor="w").grid(row=1, column=0, sticky="w", pady=3)
    entry_pb_url = tk.Entry(frame_params, width=45)
    entry_pb_url.grid(row=1, column=1, pady=3, sticky="we", columnspan=2)

    tk.Label(frame_params, text="Nombre Agenda:", anchor="w").grid(row=2, column=0, sticky="w", pady=3)
    entry_pb_name = tk.Entry(frame_params, width=45)
    entry_pb_name.grid(row=2, column=1, pady=3, sticky="we", columnspan=2)

    tk.Label(frame_params, text="URL Firmware por defecto:", anchor="w").grid(row=3, column=0, sticky="w", pady=3)
    entry_firmware_url = tk.Entry(frame_params, width=45)
    entry_firmware_url.grid(row=3, column=1, pady=3, sticky="we", columnspan=2)

    tk.Label(frame_params, text="Servidor NTP:", anchor="w").grid(row=4, column=0, sticky="w", pady=3)
    entry_sv_ntp = tk.Entry(frame_params, width=45)
    entry_sv_ntp.grid(row=4, column=1, pady=3, sticky="we", columnspan=2)

    tk.Label(frame_params, text="Zona horaria (-4 Invierno o -3 Verano):", anchor="w").grid(row=5, column=0, sticky="w", pady=3)
    entry_ltime_zone = tk.Entry(frame_params, width=45)
    entry_ltime_zone.grid(row=5, column=1, pady=3, sticky="we", columnspan=2)

    tk.Label(frame_params, text="Contraseña de user admin:", anchor="w").grid(row=6, column=0, sticky="w", pady=3)
    entry_a_pass = tk.Entry(frame_params, width=45, show="*")
    entry_a_pass.grid(row=6, column=1, pady=3, sticky="we", columnspan=2)

    # Selector de carpeta de exportación
    tk.Label(frame_params, text="Carpeta de Exportación:", anchor="w").grid(row=7, column=0, sticky="w", pady=3)
    entry_carpeta = tk.Entry(frame_params, width=33)
    entry_carpeta.grid(row=7, column=1, pady=3, sticky="we")
    entry_carpeta.insert(0, "") # Vacío por defecto

    btn_examinar = tk.Button(
        frame_params,
        text="Examinar...",
        command=lambda: seleccionar_carpeta(entry_carpeta),
        bg="#e0e0e0",
        font=("Arial", 8, "bold")
    )
    btn_examinar.grid(row=7, column=2, padx=5, pady=3)

    frame_params.columnconfigure(1, weight=1)

    # Marco para la tabla de Excel
    frame_tabla = tk.LabelFrame(root, text=" Datos de los Teléfonos ", font=("Arial", 9, "bold"), padx=10, pady=8)
    frame_tabla.pack(padx=15, pady=5, fill="both", expand=True)

    tk.Label(
        frame_tabla,
        text="Pega tus filas directamente desde Excel (Orden de Columnas: MAC | Extensión | Secret | Firmware [opcional]):",
        font=("Arial", 8),
        fg="gray"
    ).pack(anchor="w", pady=2)

    text_container = tk.Frame(frame_tabla)
    text_container.pack(fill="both", expand=True, pady=5)

    text_datos = tk.Text(text_container, height=10, font=("Consolas", 9), wrap="none")
    
    scroll_y = tk.Scrollbar(text_container, orient="vertical", command=text_datos.yview)
    scroll_x = tk.Scrollbar(text_container, orient="horizontal", command=text_datos.xview)
    
    text_datos.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)

    text_datos.grid(row=0, column=0, sticky="nsew")
    scroll_y.grid(row=0, column=1, sticky="ns")
    scroll_x.grid(row=1, column=0, sticky="ew")

    text_container.rowconfigure(0, weight=1)
    text_container.columnconfigure(0, weight=1)

    # Botón principal
    btn = tk.Button(
        root,
        text="Generar Archivos .CFG Masivamente",
        command=lambda: procesar_datos(entry_sv_ip, entry_pb_url, entry_pb_name, entry_firmware_url, entry_sv_ntp, entry_ltime_zone, entry_a_pass, entry_carpeta, text_datos),
        bg="#214778",
        fg="white",
        font=("Arial", 10, "bold"),
        padx=10,
        pady=8
    )
    btn.pack(pady=10)

    root.mainloop()