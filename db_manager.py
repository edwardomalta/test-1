from tinydb import TinyDB, Query
import datetime
import os
from shutil import copy as _cp

DB = "data.json"
DB_DIR = None

def set_path(data_dir):
	global DB_DIR
	DB_DIR = data_dir
	print(f"Path has bin set to: {data_dir}")

def get_db():
	"""Devuelve la instancia principal de TinyDB."""
	DB_PN = os.path.join(DB_DIR, DB)
	return TinyDB(DB_PN)

# ------ Tabla CONFIG (para saldo inicial, etc.) -------
def set_saldo_inicial(valor):
	db = get_db()
	config_table = db.table("config")
	config_table.upsert(
		{"key": "saldo_inicial", "value": valor},
		Query().key == "saldo_inicial"
	)

#def get_saldo_inicial():
#	db = get_db()
#	config_table = db.table("config")
#	# algo = config_table.get(doc_id=1)["saldo_inicial"]
#	algo = config_table.all()[0]["value"]
#	print("Todos los documentos: ", config_table.all())
#	#algo = config_table.get(Query().saldo_inicial.exists())["saldo_inicial"]
#	#print(algo)
#	return algo

def get_saldo_inicial():
	db = get_db()
	config_table = db.table("config")
	saldo_doc = config_table.get(Query().key == "saldo_inicial")
	if saldo_doc:
		return saldo_doc["value"]
	else:
		return None

def calc_balance_actual():
		inicial = get_saldo_inicial()
		if inicial is None:
			return None

		db = get_db()
		registros = db.all()

		ingresos = 0
		gastos = 0
		for r in registros:
			ingresos += r.get('ingreso', 0)
			gastos += r.get('gasto', 0)

		balance_actual = inicial + ingresos - gastos
		return balance_actual

# ----- Tabla MOVIMIENTOS (para ingresos/gastos) -------
def insertar_movimiento(fecha, concepto, ingreso, gasto):
	db = get_db()
	db.insert({
		"fecha": fecha,		# (yhear, month, day, hour, minute )
		"concepto": concepto,
		"gasto": gasto
		})

#def get_movimientos():
#	db = get_db()
#	return db.all()	# si guardas todo en la tabla por defecto
	# o si tienes una tabla "movimientos":
	# mov_table = db.table("movimientos")
	# return mov_table.all()

def filtrar_movimientos_por_fecha(fecha_inicial, fecha_final):
	# Ejemplo simple: filtra en Python después de obtener todos
	from datetime import datetime
	registros = get_movimientos()
	filtrados = []
	for r in registros:
		(y, m, d, hh, mm) = r['fecha']
		dt = datetime(y, m, d, hh, mm)
		if fecha_inicial <= dt <= fecha_final:
			filtrados.append(r)
	return filtrados

# Aqui vamos a extraer todos!
def get_movimientos():
	db = get_db()
	registros = db.all()
	print(f"DEBUG REGISTROS:{registros}")

	registros.sort(key=lambda m: m['fecha'])
	saldo_inicial = get_saldo_inicial() 
	balance_acumulado = saldo_inicial

	items = []

	color1 = (1, 0.3, 0.1, 1) 	# gris claro
	color2 = (0.8, 0.2, 0.05, 1)		# gris un poco más oscuro..

	for i, reg in enumerate (registros):
		año, mes, dia, hora, minuto = reg['fecha']
		fecha_str = f"{año}/{mes:02}/{dia:02} {hora:02}:{minuto:02}"

		concepto_str = reg.get('concepto', '')
		ingreso_str = str(reg.get('ingreso', 0))
		egreso_str = str(reg.get('gasto', 0))

		balance_acumulado += reg.get('ingreso', 0) - reg.get('gasto', 0)
		balance_str = str(balance_acumulado)

		bg_color = color1 if i % 2 == 0 else color2

		items.append({
			'fecha': fecha_str,
			'concepto': concepto_str,
			'ingreso': ingreso_str,
			'egreso': egreso_str,
			'balance': balance_str,
			'background_color': bg_color
			})

	return items

def backup_db(directorio=None, fname=DB):
	# Primero elegimos un lugar:
	DEFAULT_DR_BACKUP = os.getcwd()
	if not directorio:
		b = os.path.join(DEFAULT_DR_BACKUP, DB)
	else: 
		b = os.path.join(directorio, fname)
	# luego copiamos del lugar actual al lugar de destino
	a = os.path.join(DB_DIR, DB)
	_cp(a, b) #<- ESto es un ejemplo

def import_db(directorio, fname):
	# es necesario saber a donde vamos a buscar la info...
	a = os.path.join(directorio, fname)
	b = os.path.join(DB_DIR, DB)
	_cp(a, b)