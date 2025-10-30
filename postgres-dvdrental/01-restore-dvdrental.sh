#!/bin/bash
set -e

echo ""
echo "=========================================="
echo "DVD Rental Database Initialization"
echo "=========================================="
echo ""

# Función para esperar a PostgreSQL
wait_for_postgres() {
    echo "Esperando a que PostgreSQL esté listo..."
    until pg_isready -U "$POSTGRES_USER" > /dev/null 2>&1; do
        sleep 1
    done
    echo "PostgreSQL está listo"
}

# Esperar a PostgreSQL
wait_for_postgres

echo ""
echo "Verificando base de datos..."

# Verificar si la base de datos ya existe
if psql -U "$POSTGRES_USER" -lqt | cut -d \| -f 1 | grep -qw "$POSTGRES_DB"; then
    echo "La base de datos '$POSTGRES_DB' ya existe"
    
    # Verificar si tiene tablas
    TABLE_COUNT=$(psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -t -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public';")
    
    if [ "$TABLE_COUNT" -gt 0 ]; then
        echo "La base de datos ya contiene $TABLE_COUNT tablas"
        echo "Saltando restauración"
        exit 0
    fi
fi

echo ""
echo "Creando base de datos '$POSTGRES_DB'..."
psql -U "$POSTGRES_USER" -c "CREATE DATABASE $POSTGRES_DB;" 2>/dev/null || echo "Base de datos ya existe"

echo ""
echo "Restaurando DVD Rental Database desde /tmp/dvdrental.tar..."

# Restaurar la base de datos
pg_restore -U "$POSTGRES_USER" -d "$POSTGRES_DB" /tmp/dvdrental.tar --no-owner --no-acl 2>&1 | grep -v "WARNING" || true

echo ""
echo "Verificando restauración..."

# Contar tablas restauradas
TABLE_COUNT=$(psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -t -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public';")
echo "Tablas creadas: $TABLE_COUNT"

# Contar filas en algunas tablas importantes
FILM_COUNT=$(psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -t -c "SELECT COUNT(*) FROM film;")
CUSTOMER_COUNT=$(psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -t -c "SELECT COUNT(*) FROM customer;")
RENTAL_COUNT=$(psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -t -c "SELECT COUNT(*) FROM rental;")

echo "Datos cargados:"
echo "   - Películas: $FILM_COUNT"
echo "   - Clientes: $CUSTOMER_COUNT"
echo "   - Rentas: $RENTAL_COUNT"

echo ""
echo "=========================================="
echo "DVD Rental Database restaurada exitosamente"
echo "=========================================="
echo ""

# Limpiar archivo temporal
rm -f /tmp/dvdrental.tar

exit 0