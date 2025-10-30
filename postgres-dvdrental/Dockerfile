# Imagen base de PostgreSQL
FROM postgres:15

# Metadata
LABEL maintainer="Samuel Juarez <samuelj.b.190@gmail.com>"
LABEL description="PostgreSQL 15 con DVD Rental Database precargada"
LABEL version="1.0.0"

# Variables de entorno por defecto
ENV POSTGRES_DB=dvdrental \
    POSTGRES_USER=postgres \
    POSTGRES_PASSWORD=postgres

# Copiar el archivo tar de la base de datos
COPY dvdrental.tar /tmp/dvdrental.tar

# Copiar script de inicialización
COPY 01-restore-dvdrental.sh /docker-entrypoint-initdb.d/01-restore-dvdrental.sh

# Dar permisos de ejecución
RUN chmod +x /docker-entrypoint-initdb.d/01-restore-dvdrental.sh

# Exponer puerto de PostgreSQL
EXPOSE 5432

# El comando por defecto lo maneja la imagen base de postgres
# Automáticamente ejecutará los scripts en /docker-entrypoint-initdb.d/