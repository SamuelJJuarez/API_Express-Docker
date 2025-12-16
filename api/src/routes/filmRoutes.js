const express = require('express');
const router = express.Router();
const filmController = require('../controllers/filmController');

// Rutas de películas
router.get('/', filmController.getAllFilms);
// Ruta para buscar películas por título
router.get('/search', filmController.searchFilmsByTitle);
// Ruta para obtener películas por categoría
router.get('/category/:category', filmController.getFilmsByCategory);
// Ruta para obtener detalles de una película por ID
router.get('/:id', filmController.getFilmById);

module.exports = router;