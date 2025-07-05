import sqlite3

def agregar_columna_materia():
    conn = sqlite3.connect("base_datos.db")
    c = conn.cursor()
    try:
        c.execute("ALTER TABLE estudiantes ADD COLUMN materia TEXT DEFAULT ''")
        print("Columna 'materia' agregada correctamente.")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e).lower():
            print("La columna 'materia' ya existe en la tabla.")
        else:
            print("Error al agregar la columna 'materia':", e)
    conn.commit()
    conn.close()

if __name__ == "__main__":
    agregar_columna_materia()
