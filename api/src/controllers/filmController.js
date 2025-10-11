const pool = require('../config/database');

// Obtener todas las películas
const getAllFilms = async (req, res) => {
  try {
    const result = await pool.query(
      'SELECT film_id, title, description, release_year, length, rating FROM film LIMIT 20'
    );
    res.json({
      success: true,
      count: result.rows.length,
      data: result.rows
    });
  } catch (error) {
    console.error('Error al obtener películas:', error);
    res.status(500).json({
      success: false,
      message: 'Error al obtener las películas',
      error: error.message
    });
  }
};

// Obtener una película por ID
const getFilmById = async (req, res) => {
  try {
    const { id } = req.params;
    const result = await pool.query(
      'SELECT * FROM film WHERE film_id = $1',
      [id]
    );
    
    if (result.rows.length === 0) {
      return res.status(404).json({
        success: false,
        message: 'Película no encontrada'
      });
    }
    
    res.json({
      success: true,
      data: result.rows[0]
    });
  } catch (error) {
    console.error('Error al obtener película:', error);
    res.status(500).json({
      success: false,
      message: 'Error al obtener la película',
      error: error.message
    });
  }
};

// Buscar películas por título
const searchFilmsByTitle = async (req, res) => {
  try {
    const { title } = req.query;
    const result = await pool.query(
      'SELECT film_id, title, description, release_year, rating FROM film WHERE title ILIKE $1',
      [`%${title}%`]
    );
    
    res.json({
      success: true,
      count: result.rows.length,
      data: result.rows
    });
  } catch (error) {
    console.error('Error al buscar películas:', error);
    res.status(500).json({
      success: false,
      message: 'Error al buscar películas',
      error: error.message
    });
  }
};

// Obtener películas por categoría
const getFilmsByCategory = async (req, res) => {
  try {
    const { category } = req.params;
    const result = await pool.query(
      `SELECT f.film_id, f.title, f.description, f.release_year, c.name as category
       FROM film f
       JOIN film_category fc ON f.film_id = fc.film_id
       JOIN category c ON fc.category_id = c.category_id
       WHERE c.name ILIKE $1`,
      [category]
    );
    
    res.json({
      success: true,
      count: result.rows.length,
      data: result.rows
    });
  } catch (error) {
    console.error('Error al obtener películas por categoría:', error);
    res.status(500).json({
      success: false,
      message: 'Error al obtener películas por categoría',
      error: error.message
    });
  }
};

module.exports = {
  getAllFilms,
  getFilmById,
  searchFilmsByTitle,
  getFilmsByCategory
};