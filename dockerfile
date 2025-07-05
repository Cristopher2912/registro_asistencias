# Usa una imagen oficial con Python
FROM python:3.10-slim

# Instala dependencias del sistema necesarias
RUN apt-get update && apt-get install -y libgl1 libglib2.0-0 && rm -rf /var/lib/apt/lists/*

# Establece el directorio de trabajo
WORKDIR /app

# Copia los archivos del proyecto
COPY . /app

# Instala las dependencias de Python
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Expone el puerto (si usas Flask en 5000, por ejemplo)
EXPOSE 5000

# Comando para ejecutar la app
CMD ["python", "backend/app.py"]
