from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import ObjectProperty, StringProperty, ListProperty, NumericProperty
import datetime
from tinydb import TinyDB, Query
from kivy.clock import Clock
from db_manager import (get_saldo_inicial, 
						set_saldo_inicial,
						calc_balance_actual, 
						insertar_movimiento, 
						get_movimientos,
						backup_db,
						import_db,
						set_path,
						get_db)
import os

CWD = os.getcwd()

DB = "data.json"

class CustomRow(BoxLayout):
	tama_stdr = NumericProperty(14)
	background_color = ListProperty([0, 0, 0, 1])
	balance = StringProperty("$ 0.00")
	egreso = StringProperty("$ 0.00")
	ingreso = StringProperty("$ 0.00")
	concepto = StringProperty("algo")
	fecha = StringProperty("/ /")

class PopupBox(BoxLayout):
	pass

class BalancePopup(Popup):
	def validar_saldo(self):

		saldo_input = self.ids.txt_saldo_inicial.text.strip()
		
		try:
			saldo_num = float(saldo_input)
			set_saldo_inicial(saldo_num)
			self.dismiss()

		except ValueError:
			self.ids.lbl_error.text = "¡Por favor ingresa un número válido!"
			self.ids.txt_saldo_inicial.text=""

class Statistics(Screen):
	pass

class FilePopup(Popup):
	callback = ObjectProperty(None)
	cwd = CWD
	def get_file(self, path, file):
		print(path, file)
		if self.callback:
			self.callback(path, file)

class Config(Screen):
	def open_popup(self, modo):
		if modo == "respaldar":
			popup = FilePopup(title="Selecciona un lugar para respaldar")
			popup.callback = self.respaldar_db
		elif modo == "importar":
			popup = FilePopup(title="Selecciona un archivo para importar")
			popup.callback = self.importar_db
		else:
			return
		popup.open()

	def respaldar_db(self, path, file):
		# Debe seleccionar solamente una carpeta... el nombre lo ponemos nosotros
		#popup = FilePopup(title="Selecciona un lugar para respaldar")
		#popup.open()
		print(f"Respaldando en {path}")
		if not file:
			file = DB
		backup_db(path, file)


	def importar_db(self, path, file):
		# Debe seleccionar un archivo .json
		#popup = FilePopup(title="Selecciona un archivo para importar")
		#popup.open()
		print(f"Importando desde {path}")
		if not file:
			file = DB
		else:
			file = file[0] 
		import_db(path, file)

class Tabla(Screen):
	name = "tabla"
	data_items = ListProperty([])

	def on_pre_enter(self):
		"""Este método se llama justo antes de que la Screen sea mostraa.
		   Podemos aprovechar para cargar la base de datos y poblar la RecycleView."""
		self.carga_datos()

	def carga_datos(self):
		

		items = get_movimientos()

		self.data_items = items

		self.ids.rv.data = items

	def filtrar_por_mes(self):
		pass

	def filtrar_por_dia(self):
		pass

class Registro(Screen):
	concepto = ObjectProperty()
	cantidad = ObjectProperty()
	gasto = True	# Si no es gasto entonces es ingreso

	def limpiar(self):
		self.concepto.text = ""
		self.cantidad.text = ""

	def guardar(self):
		# Aqui lo había hecho antes de la db_manager así que:	
		db = get_db()

		ahora = datetime.datetime.now()
		ahora_tuple = (
			ahora.year, 
			ahora.month, 
			ahora.day, 
			ahora.hour, 
			ahora.minute
		)

		try: 
			cant = int(self.cantidad.text)
			print(f"Fecha: {ahora_tuple}; Concepto: {self.concepto.text}; Tipo gasto: {self.gasto}; Cantidad: {cant}")
			if self.gasto:
				db.insert({
					'fecha': ahora_tuple, 
					'concepto': self.concepto.text, 
					'ingreso': 0,
					'gasto': cant,
					})
			else:
				db.insert({
					'fecha': ahora_tuple, 
					'concepto': self.concepto.text, 
					'ingreso': cant,
					'gasto': 0,
					})

		except ValueError:
			print(f"Error: debes poner una cantidad!")
		except Exception as e:
			print(f"Ocurrio un error inesperado: {e}")

class Menu(Screen):
	balance = NumericProperty(None)
	
	def on_enter(self):
		self.balance = calc_balance_actual()
		if self.balance is None:
			Clock.schedule_once(self.show_popup, 0.5)

	def show_popup(self, dt):
		popup = BalancePopup()
		popup.open()	


class Manager(ScreenManager):
	pass

class FinanzasApp(App):
	def build(self):
		print(f"Setting path for db: {self.user_data_dir}")
		set_path(self.user_data_dir)
		return Manager()

if __name__ == "__main__":
	FinanzasApp().run()