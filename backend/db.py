import sqlite3
from datetime import datetime

def crear_bd():
    conn = sqlite3.connect("base_datos.db")
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS estudiantes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            foto TEXT NOT NULL,
            materia TEXT NOT NULL
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS asistencias (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            estudiante_id INTEGER,
            fecha TEXT,
            hora TEXT,
            presente INTEGER,
            FOREIGN KEY(estudiante_id) REFERENCES estudiantes(id)
        )
    ''')
    conn.commit()
    conn.close()

def agregar_estudiante(nombre, foto_path, materia):
    conn = sqlite3.connect("base_datos.db")
    c = conn.cursor()
    c.execute("INSERT INTO estudiantes (nombre, foto, materia) VALUES (?, ?, ?)", (nombre, foto_path, materia))
    conn.commit()
    conn.close()

def obtener_estudiantes():
    conn = sqlite3.connect("base_datos.db")
    c = conn.cursor()
    c.execute("SELECT id, nombre, foto, materia FROM estudiantes")
    datos = c.fetchall()
    conn.close()
    return datos

def registrar_asistencia(estudiante_id, presente):
    import sqlite3
    from datetime import datetime
    conn = sqlite3.connect("base_datos.db")
    c = conn.cursor()
    ahora = datetime.now()
    fecha = ahora.strftime('%Y-%m-%d')
    hora = ahora.strftime('%H:%M:%S')
    c.execute("INSERT INTO asistencias (estudiante_id, fecha, hora, presente) VALUES (?, ?, ?, ?)",
              (estudiante_id, fecha, hora, presente))
    conn.commit()
    conn.close()



def resumen_asistencias():
    conn = sqlite3.connect("base_datos.db")
    c = conn.cursor()
    c.execute('''
        SELECT e.id,
               e.nombre,
               SUM(CASE WHEN a.presente = 1 THEN 1 ELSE 0 END) AS total_asistencias,
               SUM(CASE WHEN a.presente = 0 THEN 1 ELSE 0 END) AS total_faltas
        FROM estudiantes e
        LEFT JOIN asistencias a ON e.id = a.estudiante_id
        GROUP BY e.id
    ''')
    datos = c.fetchall()
    conn.close()
    return datos

def detalle_asistencia(estudiante_id):
    conn = sqlite3.connect("base_datos.db")
    c = conn.cursor()
    c.execute("SELECT nombre FROM estudiantes WHERE id=?", (estudiante_id,))
    row = c.fetchone()
    if not row:
        conn.close()
        return None
    nombre = row[0]
    c.execute('''
        SELECT fecha, hora, presente FROM asistencias
        WHERE estudiante_id=?
        ORDER BY fecha DESC, hora DESC
    ''', (estudiante_id,))
    registros = c.fetchall()
    conn.close()
    lista_registros = []
    for fecha, hora, presente in registros:
        lista_registros.append({
            "fecha": fecha,
            "hora": hora,
            "presente": presente
        })
    return {
        "nombre": nombre,
        "registros": lista_registros
    }

def registrar_faltas_automaticas():
    import sqlite3
    from datetime import datetime

    conn = sqlite3.connect("base_datos.db")
    c = conn.cursor()

    hoy = datetime.now().strftime('%Y-%m-%d')

    c.execute("SELECT id FROM estudiantes")
    todos = set(r[0] for r in c.fetchall())

    c.execute("SELECT estudiante_id FROM asistencias WHERE fecha = ? AND presente = 1", (hoy,))
    asistieron = set(r[0] for r in c.fetchall())

    faltaron = todos - asistieron

    for est_id in faltaron:
        hora_actual = datetime.now().strftime('%H:%M:%S')
        c.execute("INSERT INTO asistencias (estudiante_id, fecha, hora, presente) VALUES (?, ?, ?, ?)",
                  (est_id, hoy, hora_actual, 0))

    conn.commit()
    conn.close()


    return len(ausentes)
