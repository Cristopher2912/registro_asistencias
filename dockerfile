# Usa una imagen oficial de Python slim
FROM python:3.10-slim

# Instala librerías nativas necesarias para OpenCV (libgl y libglib)
RUN apt-get update && \
    apt-get install -y libgl1 libglib2.0-0 && \
    rm -rf /var/lib/apt/lists/*

# Establece el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copia los archivos del proyecto al contenedor
COPY . /app

# Actualiza pip e instala las dependencias del proyecto
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Expone el puerto para la aplicación Flask (ajusta si usas otro puerto)
EXPOSE 5000

# Comando para ejecutar la aplicación
CMD ["python", "backend/app.py"]
