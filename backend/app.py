from flask import Flask, request, jsonify, render_template
import os
import sqlite3
from datetime import datetime
from db import crear_bd, agregar_estudiante, registrar_asistencia, resumen_asistencias, detalle_asistencia, obtener_estudiantes, registrar_faltas_automaticas
from recognizer import reconocer_estudiante


app = Flask(__name__, template_folder='../frontend', static_folder='../frontend/static')

app.config['TEMPLATES_AUTO_RELOAD'] = True  # refresca templates automáticamente

os.makedirs('static/fotos', exist_ok=True)

crear_bd()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/ingresar')
def ingresar():
    return render_template('ingresar.html')

@app.route('/asistencia')
def asistencia():
    return render_template('asistencia.html')

@app.route('/registro')
def registro():
    return render_template('registro.html')

@app.route('/estudiantes')
def estudiantes():
    return render_template('estudiantes.html')

@app.route('/api/marcar_faltas', methods=['POST'])
def marcar_faltas():
    cantidad = marcar_faltas_automaticamente()
    return jsonify({"mensaje": f"Se marcaron {cantidad} faltas automáticamente"})


@app.route('/api/ingresar_estudiante', methods=['POST'])
def subir_estudiante():
    nombre = request.form.get('nombre')
    materia = request.form.get('materia')
    foto = request.files.get('foto')

    if not nombre or not materia or not foto:
        return jsonify({"error": "Faltan datos"}), 400

    filename = nombre.replace(" ", "_") + ".jpg"
    ruta = os.path.join('static/fotos', filename)
    foto.save(ruta)

    agregar_estudiante(nombre, filename, materia)
    return jsonify({"mensaje": "Estudiante registrado correctamente"})

@app.route('/api/reconocer_asistencia', methods=['POST'])
def reconocimiento():
    data = request.get_json()
    imagen = data.get('imagen')
    resultado = reconocer_estudiante(imagen)
    if resultado:
        id_est, nombre = resultado

        # Verificar si ya registró asistencia hoy
        conn = sqlite3.connect("base_datos.db")
        c = conn.cursor()
        hoy = datetime.now().strftime('%Y-%m-%d')
        c.execute("SELECT COUNT(*) FROM asistencias WHERE estudiante_id = ? AND fecha = ? AND presente = 1", (id_est, hoy))
        ya_registrado = c.fetchone()[0]
        conn.close()

        if ya_registrado:
            print(f"[INFO] Asistencia YA registrada hoy para {nombre} (id {id_est})")
            return jsonify({"mensaje": f"Asistencia ya registrada hoy para {nombre}", "repetido": True})

        print(f"[INFO] Registrando asistencia para {nombre} (id {id_est})")
        registrar_asistencia(id_est, 1)
        print(f"[INFO] Asistencia registrada para {nombre} (id {id_est})")

        return jsonify({"mensaje": f"Asistencia registrada para {nombre}", "repetido": False})

    else:
        print("[INFO] No se reconoció el rostro")
        return jsonify({"mensaje": "No se reconoció el rostro", "repetido": True})


@app.route('/api/resumen')
def api_resumen():
    datos = resumen_asistencias()
    lista = []
    for est_id, nombre, total_asistencias, total_faltas in datos:
        lista.append({
            "estudiante_id": est_id,
            "nombre": nombre,
            "total_asistencias": total_asistencias if total_asistencias else 0,
            "total_faltas": total_faltas if total_faltas else 0
        })
    return jsonify({"resumen": lista})


@app.route('/api/estudiantes/<int:id>', methods=['PUT'])
def api_actualizar_estudiante(id):
    data = request.get_json()
    nombre = data.get('nombre')
    materia = data.get('materia')
    conn = sqlite3.connect("base_datos.db")
    c = conn.cursor()
    c.execute("UPDATE estudiantes SET nombre=?, materia=? WHERE id=?", (nombre, materia, id))
    conn.commit()
    conn.close()
    return jsonify({"mensaje": "Estudiante actualizado"})

@app.route('/api/estudiantes/<int:id>', methods=['DELETE'])
def api_eliminar_estudiante(id):
    conn = sqlite3.connect("base_datos.db")
    c = conn.cursor()
    c.execute("DELETE FROM estudiantes WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return jsonify({"mensaje": "Estudiante eliminado"})


@app.route('/api/detalle_asistencia/<int:id>')
def api_detalle_asistencia(id):
    detalle = detalle_asistencia(id)
    if detalle is None:
        return jsonify({"error": "Estudiante no encontrado"}), 404
    return jsonify(detalle)

# Nueva ruta API para obtener lista de estudiantes (sin fotos)
@app.route('/api/estudiantes')
def api_estudiantes():
    estudiantes = obtener_estudiantes()
    lista = []
    for est_id, nombre, foto, materia in estudiantes:
        lista.append({
            "id": est_id,
            "nombre": nombre,
            "materia": materia if materia else ""
            # No incluimos foto para no enviar imagen
        })
    return jsonify({"estudiantes": lista})

@app.route('/api/entrenar_modelo', methods=['POST'])
def api_entrenar_modelo():
    from recognizer import entrenar_reconocedor
    exito = entrenar_reconocedor()
    return jsonify({"mensaje": "Modelo entrenado correctamente" if exito else "Falló el entrenamiento"})



@app.route('/api/registrar_faltas', methods=['POST'])
def api_registrar_faltas():
    registrar_faltas_automaticas()
    return jsonify({"mensaje": "Faltas registradas correctamente"})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
