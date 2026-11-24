import csv
import os

BASE = os.path.dirname(os.path.abspath(__file__))
DATOS = os.path.join(BASE, "datos")
os.makedirs(DATOS, exist_ok=True)

AREAS = ["Soporte Tecnico", "Gerencia de Operaciones/Riesgo", "Atencion al Cliente"]
PRIORIDADES = ["Alta", "Media", "Baja"]

RECLAMOS = [
    # Soporte Tecnico / Alta
    ("No puedo acceder a la aplicacion movil, se cierra cada vez que intento iniciar sesion", "Soporte Tecnico", "Alta"),
    ("La app se congela al hacer una transferencia y no responde", "Soporte Tecnico", "Alta"),
    ("No puedo iniciar sesion en la aplicacion, me dice que la contrasena es invalida", "Soporte Tecnico", "Alta"),
    ("La aplicacion se cierra sola al abrirla, no puedo usarla", "Soporte Tecnico", "Alta"),
    ("Olvide mi contrasena y no puedo recuperarla por la app", "Soporte Tecnico", "Alta"),
    ("No puedo registrar mi usuario en la aplicacion movil", "Soporte Tecnico", "Alta"),
    ("La app no carga los saldos de mis cuentas", "Soporte Tecnico", "Alta"),
    ("No puedo activar mi tarjeta desde la aplicacion", "Soporte Tecnico", "Alta"),
    ("Error de conexion constante en la aplicacion movil", "Soporte Tecnico", "Alta"),
    ("La camara no funciona para depositar cheques por la app", "Soporte Tecnico", "Alta"),
    ("No puedo actualizar mis datos personales en la app", "Soporte Tecnico", "Alta"),
    ("La aplicacion no me deja generar claves dinamicas", "Soporte Tecnico", "Alta"),
    ("No puedo descargar mis estados de cuenta desde la app", "Soporte Tecnico", "Alta"),
    ("La app me da error al intentar pagar servicios", "Soporte Tecnico", "Alta"),
    ("No puedo configurar alertas en la aplicacion movil", "Soporte Tecnico", "Alta"),
    ("La aplicacion se reinicia sola cuando hago un pago", "Soporte Tecnico", "Alta"),
    ("No puedo escanear el codigo QR para pagar", "Soporte Tecnico", "Alta"),
    ("La app no sincroniza mis movimientos bancarios", "Soporte Tecnico", "Alta"),
    ("No puedo cambiar mi numero de telefono en la app", "Soporte Tecnico", "Alta"),
    ("La aplicacion me bloquea el acceso despues de varios intentos", "Soporte Tecnico", "Alta"),
    ("La app se cierra al intentar iniciar sesion con huella", "Soporte Tecnico", "Alta"),
    ("No puedo recibir codigos de verificacion por SMS en la app", "Soporte Tecnico", "Alta"),
    ("La aplicacion no deja vincular mi cuenta bancaria", "Soporte Tecnico", "Alta"),
    ("Error al generar el token de seguridad en la app movil", "Soporte Tecnico", "Alta"),
    ("No puedo restablecer mi contrasena desde la aplicacion", "Soporte Tecnico", "Alta"),

    # Gerencia de Operaciones/Riesgo / Alta
    ("Hice una transferencia pero el dinero no llego a la cuenta del destinatario", "Gerencia de Operaciones/Riesgo", "Alta"),
    ("Un cargo no reconocido aparecio en mi cuenta bancaria", "Gerencia de Operaciones/Riesgo", "Alta"),
    ("Me debitaron dos veces el mismo pago en mi tarjeta", "Gerencia de Operaciones/Riesgo", "Alta"),
    ("No reconozco un movimiento en mi estado de cuenta", "Gerencia de Operaciones/Riesgo", "Alta"),
    ("Mi cuenta fue bloqueada por actividad sospechosa sin motivo", "Gerencia de Operaciones/Riesgo", "Alta"),
    ("Detecto una transferencia que no hice desde mi cuenta", "Gerencia de Operaciones/Riesgo", "Alta"),
    ("Me cobraron una comision que no correspondia", "Gerencia de Operaciones/Riesgo", "Alta"),
    ("Mi dinero desaparecio de la cuenta de ahorros", "Gerencia de Operaciones/Riesgo", "Alta"),
    ("Una transaccion fallo pero igual me descontaron el dinero", "Gerencia de Operaciones/Riesgo", "Alta"),
    ("Mi cuenta muestra un saldo negativo sin que haya hecho gastos", "Gerencia de Operaciones/Riesgo", "Alta"),
    ("Hice un deposito en efectivo pero no se refleja en mi cuenta", "Gerencia de Operaciones/Riesgo", "Alta"),
    ("Mi tarjeta fue clonada y hay cargos que no reconozco", "Gerencia de Operaciones/Riesgo", "Alta"),
    ("Una transferencia inmediata nunca llego y me cobraron el servicio", "Gerencia de Operaciones/Riesgo", "Alta"),
    ("Me descontaron el pago de un servicio que nunca contrate", "Gerencia de Operaciones/Riesgo", "Alta"),
    ("Mi cuenta fue vulnerada y hicieron retiros no autorizados", "Gerencia de Operaciones/Riesgo", "Alta"),
    ("Una transferencia no llego y me cobraron el costo del servicio", "Gerencia de Operaciones/Riesgo", "Alta"),
    ("Detecto retiros no autorizados en mi cuenta de ahorros", "Gerencia de Operaciones/Riesgo", "Alta"),
    ("Mi tarjeta de credito muestra cargos que no hice", "Gerencia de Operaciones/Riesgo", "Alta"),
    ("Una transferencia inmediata nunca fue acreditada", "Gerencia de Operaciones/Riesgo", "Alta"),
    ("Me bloquearon la cuenta sin previo aviso ni explicacion", "Gerencia de Operaciones/Riesgo", "Alta"),

    # Atencion al Cliente / Baja
    ("Quisiera saber el horario de atencion de la sucursal mas cercana", "Atencion al Cliente", "Baja"),
    ("Cuales son los requisitos para abrir una cuenta de ahorros", "Atencion al Cliente", "Baja"),
    ("Como puedo solicitar una tarjeta de credito adicional", "Atencion al Cliente", "Baja"),
    ("Me gustaria saber la tasa de interes de un credito hipotecario", "Atencion al Cliente", "Baja"),
    ("Donde puedo encontrar el cajero automatico mas cercano", "Atencion al Cliente", "Baja"),
    ("Como actualizar mi direccion de domicilio en el banco", "Atencion al Cliente", "Baja"),
    ("Quiero saber los beneficios de mi paquete bancario", "Atencion al Cliente", "Baja"),
    ("Como puedo solicitar una chequera para mi cuenta", "Atencion al Cliente", "Baja"),
    ("Cuales son los horarios de atencion telefonica del banco", "Atencion al Cliente", "Baja"),
    ("Como puedo bloquear temporalmente mi tarjeta", "Atencion al Cliente", "Baja"),
    ("Quiero saber si mi cuenta tiene costo de mantenimiento", "Atencion al Cliente", "Baja"),
    ("Como consultar mis puntos acumulados del programa de lealtad", "Atencion al Cliente", "Baja"),
    ("Me gustaria conocer los requisitos para un credito personal", "Atencion al Cliente", "Baja"),
    ("Como puedo recibir mis estados de cuenta por correo electronico", "Atencion al Cliente", "Baja"),
    ("Quiero saber los tipos de cuenta que ofrece el banco", "Atencion al Cliente", "Baja"),
    ("Donde esta ubicada la sucursal mas cercana a mi domicilio", "Atencion al Cliente", "Baja"),
    ("Cuales son los documentos necesarios para abrir una cuenta", "Atencion al Cliente", "Baja"),
    ("Como puedo solicitar una tarjeta de debito adicional", "Atencion al Cliente", "Baja"),
    ("Quiero saber el horario de atencion de los cajeros automaticos", "Atencion al Cliente", "Baja"),
    ("Como puedo consultar mi saldo disponible por telefono", "Atencion al Cliente", "Baja"),

    # Soporte Tecnico / Media
    ("La aplicacion movil carga muy lenta en mi celular", "Soporte Tecnico", "Media"),
    ("No puedo subir una foto de perfil en la app bancaria", "Soporte Tecnico", "Media"),
    ("La app no me permite ver el detalle de mis movimientos", "Soporte Tecnico", "Media"),
    ("No recibo los mensajes de confirmacion por SMS", "Soporte Tecnico", "Media"),
    ("La aplicacion no funciona en mi dispositivo android", "Soporte Tecnico", "Media"),
    ("No puedo cerrar sesion correctamente de la app", "Soporte Tecnico", "Media"),
    ("La app consume demasiada bateria de mi telefono", "Soporte Tecnico", "Media"),
    ("No puedo cambiar el idioma de la aplicacion movil", "Soporte Tecnico", "Media"),
    ("La app no me deja ver mis tarjetas asociadas", "Soporte Tecnico", "Media"),
    ("Error al validar mi identidad en la aplicacion", "Soporte Tecnico", "Media"),
    ("La app se traba cuando intento ver mis movimientos", "Soporte Tecnico", "Media"),
    ("No puedo actualizar la aplicacion a la ultima version", "Soporte Tecnico", "Media"),
    ("La app no reconoce mi dispositivo como de confianza", "Soporte Tecnico", "Media"),
    ("Error al sincronizar mis contactos con la aplicacion", "Soporte Tecnico", "Media"),

    # Gerencia de Operaciones/Riesgo / Media
    ("Quiero impugnar un cargo que no realice en mi cuenta", "Gerencia de Operaciones/Riesgo", "Media"),
    ("Solicito la devolucion de un cargo duplicado en mi tarjeta", "Gerencia de Operaciones/Riesgo", "Media"),
    ("Mi cuenta tiene un saldo que no corresponde a mis movimientos", "Gerencia de Operaciones/Riesgo", "Media"),
    ("No se proceso correctamente mi pago de servicios", "Gerencia de Operaciones/Riesgo", "Media"),
    ("Quiero reclamar un retraso en una transferencia interbancaria", "Gerencia de Operaciones/Riesgo", "Media"),
    ("Me cobraron intereses que no debian aplicarse", "Gerencia de Operaciones/Riesgo", "Media"),
    ("Una transferencia programada no se ejecuto en la fecha indicada", "Gerencia de Operaciones/Riesgo", "Media"),
    ("Mi cheque depositado no fue acreditado a mi cuenta", "Gerencia de Operaciones/Riesgo", "Media"),

    # Atencion al Cliente / Media
    ("Como puedo solicitar una aumento de limite de credito", "Atencion al Cliente", "Media"),
    ("Quiero saber que documentos necesito para abrir una cuenta", "Atencion al Cliente", "Media"),
    ("Como puedo hablar con un ejecutivo de cuenta", "Atencion al Cliente", "Media"),
    ("Cuales son las comisiones por transferencias internacionales", "Atencion al Cliente", "Media"),
    ("Como puedo cancelar una tarjeta de credito", "Atencion al Cliente", "Media"),
    ("Quiero saber como funciona el seguro de mi tarjeta", "Atencion al Cliente", "Media"),
    ("Como solicitar una tarjeta adicional para un familiar", "Atencion al Cliente", "Media"),
    ("Quiero cambiar el correo electronico asociado a mi cuenta", "Atencion al Cliente", "Media"),
    ("Como puedo aumentar el limite diario de mi cuenta", "Atencion al Cliente", "Media"),
    ("Quiero saber los requisitos para un credito automotriz", "Atencion al Cliente", "Media"),
    ("Como puedo contactar al servicio de atencion al cliente", "Atencion al Cliente", "Media"),

    # Soporte Tecnico / Baja
    ("La aplicacion no me permite guardar mis contactos frecuentes", "Soporte Tecnico", "Baja"),
    ("No puedo cambiar el fondo de pantalla de la app", "Soporte Tecnico", "Baja"),
    ("La app no me permite activar el modo oscuro", "Soporte Tecnico", "Baja"),
    ("No puedo configurar el bloqueo por huella digital en la app", "Soporte Tecnico", "Baja"),
    ("La aplicacion no muestra correctamente mi nombre de usuario", "Soporte Tecnico", "Baja"),
    ("La app no me permite cambiar mi foto de perfil", "Soporte Tecnico", "Baja"),
    ("No puedo activar las notificaciones push en la aplicacion", "Soporte Tecnico", "Baja"),

    # Gerencia de Operaciones/Riesgo / Baja
    ("Quiero saber el estado de una reclamacion que presente hace dias", "Gerencia de Operaciones/Riesgo", "Baja"),
    ("Como puedo presentar una queja formal ante el banco", "Gerencia de Operaciones/Riesgo", "Baja"),
    ("Quiero solicitar una investigacion sobre un movimiento estranho", "Gerencia de Operaciones/Riesgo", "Baja"),
    ("Como puedo saber si una transferencia fue recibida correctamente", "Gerencia de Operaciones/Riesgo", "Baja"),
    ("Quiero reportar un posible error en mi estado de cuenta", "Gerencia de Operaciones/Riesgo", "Baja"),
    ("Quiero saber el estado de una queja enviada al banco", "Gerencia de Operaciones/Riesgo", "Baja"),
    ("Como presento una reclamacion por un cargo indevido", "Gerencia de Operaciones/Riesgo", "Baja"),

    # Atencion al Cliente / Alta
    ("Necesito ayuda urgente para recuperar mi cuenta bloqueada", "Atencion al Cliente", "Alta"),
    ("No puedo comunicarme con un ejecutivo, necesito soporte inmediato", "Atencion al Cliente", "Alta"),
    ("Mi cuenta esta comprometida y necesito bloquearla ya", "Atencion al Cliente", "Alta"),
    ("Necesito asistencia inmediata con mi tarjeta perdida", "Atencion al Cliente", "Alta"),
    ("No puedo acceder a mi cuenta y tengo un pago urgente", "Atencion al Cliente", "Alta"),
    ("Necesito bloquear mi cuenta de forma urgente por robo", "Atencion al Cliente", "Alta"),
    ("Mi tarjeta fue robada y necesito cancelarla inmediatamente", "Atencion al Cliente", "Alta"),
]

data = []
for area in AREAS:
    for prioridad in PRIORIDADES:
        grupo = [r for r in RECLAMOS if r[1] == area and r[2] == prioridad]
        while len(grupo) < 50:
            base = grupo[len(grupo) % len(grupo)] if grupo else ("Consulta general sobre el servicio", area, prioridad)
            texto = base[0] + f" (consulta {len(grupo)+1})"
            grupo.append((texto, area, prioridad))
        data.extend(grupo[:50])

csv_path = os.path.join(DATOS, "reclamos.csv")
with open(csv_path, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["texto", "area", "prioridad"])
    for texto, area, prioridad in data:
        writer.writerow([texto, area, prioridad])

print(f"CSV generado: {csv_path} con {len(data)} filas")
