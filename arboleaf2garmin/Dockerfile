# Usar una imagen base slim de Python 3.11
FROM python:3.11-slim

# Establecer el directorio de trabajo
WORKDIR /app

COPY requirements.txt /app/requirements.txt
# Instalar las dependencias necesarias (si las hay)
RUN pip install -r requirements.txt

# TESTS
RUN apt-get update && apt-get install -y iputils-ping

# Copiar el archivo .env al contenedor
COPY .env /app/.env

# Copiar resto de archivos del proyecto al contenedor
COPY . /app

# Ejecutar el script de Python
CMD ["python", "arboleaf2garmin.py"]
