# Usar Node.js versión LTS normal (Debian)
FROM node:18

# Metadata de la imagen
LABEL maintainer="Samuel Juarez <samuelj.b.190@gmail.com>"
LABEL description="DVD Rental API - Sistema de gestión de rentas de DVDs"
LABEL version="1.0.0"

# Crear directorio de trabajo
WORKDIR /app

# Copiar archivos de dependencias
COPY package*.json ./

# Instalar dependencias de producción
RUN npm ci --only=production

# Copiar el código fuente
COPY src/ ./src/

# Crear usuario no-root por seguridad
RUN groupadd -r nodejs --gid=1001 && \
    useradd -r -g nodejs --uid=1001 -m -s /bin/bash nodejs && \
    chown -R nodejs:nodejs /app

# Cambiar a usuario no-root
USER nodejs

# Exponer el puerto
EXPOSE 3000

# Healthcheck
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD node -e "require('http').get('http://localhost:3000/', (r) => {process.exit(r.statusCode === 200 ? 0 : 1)})"

# Comando de inicio
CMD ["node", "src/index.js"]