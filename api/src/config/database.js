const { Pool } = require('pg');
require('dotenv').config();

const pool = new Pool({
  host: process.env.DB_HOST,
  port: process.env.DB_PORT,
  user: process.env.DB_USER,
  password: process.env.DB_PASSWORD,
  database: process.env.DB_NAME,
  // Configuraciones adicionales para Docker
  max: 20,
  idleTimeoutMillis: 30000,
  connectionTimeoutMillis: 10000,
});

// Configurar zona horaria para cada conexión
pool.on('connect', (client) => {
  client.query("SET timezone = 'America/Mexico_City'");
});

// Función para conectar con reintentos
const connectWithRetry = async (maxRetries = 5, delay = 5000) => {
  for (let i = 0; i < maxRetries; i++) {
    try {
      const client = await pool.connect();
      console.log('Conectado a la base de datos PostgreSQL');
      client.release();
      return;
    } catch (err) {
      console.log(`Intento ${i + 1}/${maxRetries} - Error al conectar a la base de datos:`, err.message);
      if (i < maxRetries - 1) {
        console.log(`Reintentando en ${delay/1000} segundos...`);
        await new Promise(resolve => setTimeout(resolve, delay));
      }
    }
  }
  console.error('No se pudo conectar a la base de datos después de varios intentos');
};

// Intentar conectar al iniciar
connectWithRetry();

pool.on('error', (err) => {
  console.error('Error inesperado en el pool de conexiones:', err);
});

module.exports = pool;