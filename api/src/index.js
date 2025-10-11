const express = require('express');
const cors = require('cors');
require('dotenv').config();

const filmRoutes = require('./routes/filmRoutes');

const app = express();
const PORT = process.env.PORT || 3000;

// Middlewares
app.use(cors());
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Ruta de prueba
app.get('/', (req, res) => {
  res.json({
    message: '🎬 Bienvenido a la API de DVD Rental',
    endpoints: {
      films: '/api/films',
      filmById: '/api/films/:id',
      searchFilms: '/api/films/search?title=palabra',
      filmsByCategory: '/api/films/category/:category'
    }
  });
});

// Rutas
app.use('/api/films', filmRoutes);

// Manejo de rutas no encontradas
app.use((req, res) => {
  res.status(404).json({
    success: false,
    message: 'Ruta no encontrada'
  });
});

// Iniciar servidor
app.listen(PORT, () => {
  console.log(`🚀 Servidor corriendo en http://localhost:${PORT}`);
});