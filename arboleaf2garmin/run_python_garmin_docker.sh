#!/bin/bash

# Nombre del servicio definido en docker-compose.yml
NOMBRE_SERVICIO="python-garmin"

# Verificar si el contenedor está en ejecución
if [ "$(docker ps -q -f name=$NOMBRE_SERVICIO)" ]; then
    echo "El contenedor $NOMBRE_SERVICIO ya está en ejecución."
else
    echo "El contenedor $NOMBRE_SERVICIO no está en ejecución. Iniciando..."
    
    # Navegar al directorio del proyecto
    cd /home/xbmc/docker/python-garmin/

    # Ejecutar Docker Compose
    docker compose up -d
fi
