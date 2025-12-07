# DVD Rental API
**Hecho por Samuel Juárez, Leonardo Rosas y Jesús González**

API REST para gestión de rentas de DVDs con PostgreSQL.

## Instalación

### Opción 1: Docker Compose (Recomendado)
```bash
curl -o docker-compose.yml https://raw.githubusercontent.com/SamuelJJuarez/API_Express-Docker/main/distribution/docker-compose.yml
docker-compose up -d
```

### Opción 2: Comandos Docker
```bash
# Crear red
docker network create dvdrental-network

# PostgreSQL
docker run -d --name dvdrental-db --network dvdrental-network -p 5432:5432 samueljjuarezb/postgres-dvdrental:latest

# API
docker run -d --name dvdrental-api --network dvdrental-network -e DB_HOST=dvdrental-db -p 3000:3000 samueljjuarezb/dvdapi-express-sjr:latest
```

**API disponible en:** `http://localhost:3000`

---

## Imágenes Docker

### API REST
```bash
docker pull samueljjuarezb/dvdapi-express-sjr:latest
```

### PostgreSQL + DVD Rental
```bash
docker pull samueljjuarezb/postgres-dvdrental:latest
```

## API Endpoints

**Base URL:** `http://localhost:3000`

### Películas
```
GET    /api/films                              # Listar todas
GET    /api/films/:id                          # Por ID
GET    /api/films/search?title=palabra         # Buscar
GET    /api/films/category/:category           # Por categoría
```

### Clientes
```
GET    /api/customers                          # Listar todos
GET    /api/customers/:id                      # Por ID
```

### Staff
```
GET    /api/staff                              # Listar todos
GET    /api/staff/:id                          # Por ID
```

### Rentas
```
GET    /api/rentals                            # Listar todas
POST   /api/rentals                            # Crear (requiere: customer_id, film_id, staff_id)
PUT    /api/rentals/:id/return                 # Devolver
DELETE /api/rentals/:id                        # Cancelar
GET    /api/rentals/customer/:customer_id      # Por cliente
```

### Reportes
```
GET    /api/reports/unreturned-dvds            # DVDs no devueltos
GET    /api/reports/most-rented?limit=10       # Más rentados
GET    /api/reports/staff-revenue              # Ganancias totales
GET    /api/reports/staff-revenue/:staff_id    # Ganancias por staff
GET    /api/reports/customer-rentals/:id       # Historial de cliente
```

---

## Variables de Entorno

### API
| Variable | Default |
|----------|---------|
| `DB_HOST` | `localhost` |
| `DB_PORT` | `5432` |
| `DB_USER` | `postgres` |
| `DB_PASSWORD` | `postgres` |
| `DB_NAME` | `dvdrental` |
| `PORT` | `3000` |

### PostgreSQL
| Variable | Default |
|----------|---------|
| `POSTGRES_USER` | `postgres` |
| `POSTGRES_PASSWORD` | `postgres` |
| `POSTGRES_DB` | `dvdrental` |

---

## Comandos Útiles
# Reiniciar
docker restart dvdrental-api

# Detener
docker-compose down

# Eliminar todo (incluyendo datos)
docker-compose down -v

---

## Recursos

- **Repositorio:** [GitHub](https://github.com/SamuelJJuarez/API_Express-Docker)
- **API:** [Docker Hub](https://hub.docker.com/r/samueljjuarezb/dvdapi-express-sjr)
- **PostgreSQL:** [Docker Hub](https://hub.docker.com/r/samueljjuarezb/postgres-dvdrental)
