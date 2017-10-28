# -----------------------------------------------------------------------------
# Parcial de Estructura de Datos (2° Cuatr. 2017)
#
# -	Alumno: Federico H. Cacace
# -	Profesor: Leandro E. Colombo Viña
# -----------------------------------------------------------------------------

from flask import Flask, render_template, redirect, url_for, flash, session
from flask_bootstrap import Bootstrap
from flask_script import Manager
import formularios, consultas, db

# Creando objetos flask:
app = Flask(__name__)
manager = Manager(app)
bs = Bootstrap(app)


# Constantes con nombres y rutas de archivos:
RUTA = ""
ARC_CSV = RUTA + "archivo.csv"
ERROR = RUTA + "error.log"
USER_CLAVE = RUTA + "usuario_clave.csv"


# App:
app.config["BOOTSTRAP_SERVE_LOCAL"] = True 			# Para activar versión local de Bootstrap.
app.config["SECRET_KEY"] = "UnaClaveSecreta"		# Clave random para formularios con Flask-WTF.


# Funciones:
@app.route("/index", methods=["GET", "POST"])
@app.route("/", methods=["GET", "POST"])
def inicio():
	""" Función que lleva a inicio.html o usuario.html según condiciones. """
	
	log = formularios.Login()
	if log.validate_on_submit():			# Si se presiona el botón enviar...

		bd = db.DB(USER_CLAVE)
		user, clave = bd.chequear(log.usuario.data, log.clave.data)
		if user:
			if clave:
				session["user"] = log.usuario.data
				return redirect(url_for("usuario"))

			else:							# Si la clave no corresponde con ese usuario...
				mensaje = "Contraseña inválida para <b>{}</b>".format(log.usuario.data)
				return render_template("inicio.html", login=log, info=mensaje)

		else:								# Si el usuario no existe en la DB...
			mensaje = "<b>{}</b> no es un usuario registrado".format(log.usuario.data)
			return render_template("inicio.html", login=log, info=mensaje)


	# Si existe algún 'user' en session:
	if session.get("user"):
		return redirect(url_for("usuario"))

	# En caso de ingresar por primera vez:
	return render_template("inicio.html", login=log)


@app.route("/Usuario", methods=["GET", "POST"])
def usuario():
	""" Función que lleva a usuario.html o inicio.html según condición. """

	if session.get("user"):					# Si existe algún 'user' en session...
		consulta = consultas.Consultas(ARC_CSV, ERROR)
		resultados, nro_filas, cantidad = consulta.ultimos_resultados(5)

		return render_template("usuario.html",
								resultados=resultados,
								nro_filas=nro_filas,
								cantidad=cantidad)

	else:									# En caso contrario...
		return redirect(url_for("inicio"))


@app.route("/ProductosXCliente", methods=["GET", "POST"])
def pxc():
	""" Función que lleva a pxc.html o inicio.html según condición. """

	# Si existe 'user' en sesión:
	if session.get("user"):
		busqueda = formularios.Busqueda()

		# Si se presiona el botón 'enviar':
		if busqueda.validate_on_submit():

			# Obteniendo palabra desde el StringField del formulario:
			palabra = busqueda.buscar.data.lower()

			# Si la palabre tiene menos de 3 letras...
			if len(palabra) < 3:
				error = "Debe ingresar 3 o más letras para poder realizar la búsqueda"
				return render_template("pxc.html",
										busqueda=busqueda,
										error=error)
			# Si tiene más de 3 letras:
			else:
				consulta = consultas.Consultas(ARC_CSV, ERROR)

				# Se obtiene resultados y se renderiza:
				resultados, columnas = consulta.listar_x_en_y("PRODUCTO", "CLIENTE", palabra)
				
				# Si hubo resultados:
				if len(resultados) > 1:
					return render_template("pxc.html",
											busqueda=busqueda,
											resultados=resultados,
											columnas=columnas)
				else:
					error = "No hubo resultados"
					return render_template("pxc.html",
											busqueda=busqueda,
											error=error)					

		# Si no se envia aún ninguna búsqueda:
		return render_template("pxc.html", busqueda=busqueda)

	# Si no hay sesión abierta, se vuelve a inicio.html:
	else:
		return redirect(url_for("inicio"))


@app.route("/ClientesXProducto", methods=["GET", "POST"])
def cxp():
	""" Función que lleva a cxp.html o inicio.html según condición. """

	# Si existe 'user' en sesión:
	if session.get("user"):
		busqueda = formularios.Busqueda()

		# Si se presiona el botón 'enviar':
		if busqueda.validate_on_submit():
			
			# Obteniendo palabra desde el StringField del formulario:
			palabra = busqueda.buscar.data.lower()
			
			# Si la palabre tiene menos de 3 letras...
			if len(palabra) < 3:
				error = "Debe ingresar 3 o más letras para poder realizar la búsqueda"
				return render_template("cxp.html",
										busqueda=busqueda,
										error=error)
			# Si tiene más de 3 letras:
			else:
				consulta = consultas.Consultas(ARC_CSV, ERROR)

				# Se obtiene resultados y se renderiza:
				resultados, columnas = consulta.listar_x_en_y("CLIENTE", "PRODUCTO", palabra)

				# Si hubo resultados:
				if len(resultados) > 1:
					return render_template("cxp.html",
											busqueda=busqueda,
											resultados=resultados,
											columnas=columnas)
				else:
					error = "No hubo resultados"
					return render_template("cxp.html",
											busqueda=busqueda,
											error=error)
		
		# Si no se envia aún ninguna búsqueda:
		return render_template("cxp.html", busqueda=busqueda)

	# Si no hay sesión abierta, se vuelve a inicio.html:
	else:
		return redirect(url_for("inicio"))


@app.route("/ProductosMasVendidos", methods=["GET", "POST"])
def pmv():
	""" Función que lleva a pmv.html o inicio.html según condición. """

	if session.get("user"):					# Si existe algún 'user' en session...
		return render_template("pmv.html")
	else:									# En caso contrario se vuelve a inicio.
		return redirect(url_for("inicio"))


@app.route("/ClientesMasGastaron", methods=["GET", "POST"])
def cmg():
	""" Función que lleva a cmg.html o inicio.html según condición. """

	if session.get("user"):						# Si existe algún 'user' en session...
		return render_template("cmg.html")
	else:										# En caso contrario...
		return redirect(url_for("inicio"))


@app.route("/salir")
def salir():
	""" Función que desloguea al usuario actual y redirige a inicio. """

	if session.get("user"):						# Si existe algún 'user' en session...
		session.pop("user", None)
		flash("Usuario deslogueado")

	return redirect(url_for("inicio"))			# En cualquier caso se redirige a inicio.html.


@app.errorhandler(404)
def no_encontrado(e):
	""" Función que redirige a 404.html en caso de no encontrar la página solicitada. """
	return render_template("404.html"), 404


@app.errorhandler(500)
def error_servidor(e):
	""" Función que redirige a 500.html en caso de surgir algún error en el servidor. """
	return render_template("500.html"), 500


# Iniciando:
if __name__ == "__main__":
	manager.run()


# FIN