const express = require('express');
const router = express.Router();
const filmController = require('../controllers/filmController');

// Rutas de películas
router.get('/', filmController.getAllFilms);
router.get('/search', filmController.searchFilmsByTitle);
router.get('/category/:category', filmController.getFilmsByCategory);
router.get('/:id', filmController.getFilmById);

module.exports = router;