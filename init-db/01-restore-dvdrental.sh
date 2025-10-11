#!/bin/bash
set -e

# Esperar a que PostgreSQL esté listo
until pg_isready -U postgres; do
  echo "Esperando a PostgreSQL..."
  sleep 2
done

# Crear la base de datos
psql -U postgres -c "CREATE DATABASE dvdrental;"

# Restaurar el backup
pg_restore -U postgres -d dvdrental /docker-entrypoint-initdb.d/dvdrental.tar

echo "Base de datos DVD Rental restaurada exitosamente!"