# Usa una imagen oficial ligera con Python
FROM python:3.10-slim

# Instala dependencias del sistema necesarias para OpenCV
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Establece el directorio de trabajo
WORKDIR /app

# Copia los archivos del proyecto
COPY . /app

# Actualiza pip e instala dependencias de Python
RUN pip install --upgrade pip

# Instala opencv-contrib-python para tener cv2.face y demás paquetes
RUN pip install opencv-contrib-python==4.7.0.72

# Instala las demás dependencias de tu proyecto si tienes requirements.txt
# Si tienes, usa esta línea:
RUN pip install -r requirements.txt

# Exponer puerto (ajusta según tu app)
EXPOSE 5000

# Comando para iniciar la app
CMD ["python", "backend/app.py"]
