const pool = require('../config/database');

// Obtener todas las películas (actualizado con más información)
const getAllFilms = async (req, res) => {
  try {
    const { 
      limit = 20, 
      offset = 0, 
      rating, 
      category,
      min_length,
      max_length 
    } = req.query;

    let query = `
      SELECT 
        f.film_id,
        f.title,
        f.description,
        f.release_year,
        f.length,
        f.rating,
        f.rental_rate,
        f.rental_duration,
        f.replacement_cost,
        c.name as category,
        l.name as language,
        COUNT(DISTINCT i.inventory_id) as total_copies,
        COUNT(CASE WHEN r.return_date IS NULL THEN 1 END) as rented_copies,
        COUNT(DISTINCT i.inventory_id) - COUNT(CASE WHEN r.return_date IS NULL THEN 1 END) as available_copies
      FROM film f
      LEFT JOIN film_category fc ON f.film_id = fc.film_id
      LEFT JOIN category c ON fc.category_id = c.category_id
      LEFT JOIN language l ON f.language_id = l.language_id
      LEFT JOIN inventory i ON f.film_id = i.film_id
      LEFT JOIN rental r ON i.inventory_id = r.inventory_id AND r.return_date IS NULL
    `;

    const params = [];
    const conditions = [];

    if (rating) {
      conditions.push(`f.rating = $${params.length + 1}`);
      params.push(rating);
    }

    if (category) {
      conditions.push(`c.name ILIKE $${params.length + 1}`);
      params.push(category);
    }

    if (min_length) {
      conditions.push(`f.length >= $${params.length + 1}`);
      params.push(min_length);
    }

    if (max_length) {
      conditions.push(`f.length <= $${params.length + 1}`);
      params.push(max_length);
    }

    if (conditions.length > 0) {
      query += ' WHERE ' + conditions.join(' AND ');
    }

    query += `
      GROUP BY f.film_id, f.title, f.description, f.release_year, 
               f.length, f.rating, f.rental_rate, f.rental_duration,
               f.replacement_cost, c.name, l.name
      ORDER BY f.title
      LIMIT $${params.length + 1} OFFSET $${params.length + 2}
    `;

    params.push(limit, offset);

    const result = await pool.query(query, params);

    // Obtener el total de películas
    const countQuery = `
      SELECT COUNT(DISTINCT f.film_id) as total
      FROM film f
      LEFT JOIN film_category fc ON f.film_id = fc.film_id
      LEFT JOIN category c ON fc.category_id = c.category_id
      ${conditions.length > 0 ? 'WHERE ' + conditions.join(' AND ') : ''}
    `;
    
    const countResult = await pool.query(countQuery, params.slice(0, -2));

    res.json({
      success: true,
      total: parseInt(countResult.rows[0].total),
      count: result.rows.length,
      limit: parseInt(limit),
      offset: parseInt(offset),
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

// Obtener una película por ID (actualizado)
const getFilmById = async (req, res) => {
  try {
    const { id } = req.params;
    
    const result = await pool.query(
      `SELECT 
        f.*,
        c.name as category,
        l.name as language,
        COUNT(DISTINCT i.inventory_id) as total_copies,
        COUNT(CASE WHEN r.return_date IS NULL THEN 1 END) as rented_copies,
        COUNT(DISTINCT i.inventory_id) - COUNT(CASE WHEN r.return_date IS NULL THEN 1 END) as available_copies,
        COUNT(DISTINCT r.rental_id) as total_rentals
      FROM film f
      LEFT JOIN film_category fc ON f.film_id = fc.film_id
      LEFT JOIN category c ON fc.category_id = c.category_id
      LEFT JOIN language l ON f.language_id = l.language_id
      LEFT JOIN inventory i ON f.film_id = i.film_id
      LEFT JOIN rental r ON i.inventory_id = r.inventory_id
      WHERE f.film_id = $1
      GROUP BY f.film_id, c.name, l.name`,
      [id]
    );
    
    if (result.rows.length === 0) {
      return res.status(404).json({
        success: false,
        message: 'Película no encontrada'
      });
    }

    // Obtener actores de la película
    const actorsResult = await pool.query(
      `SELECT a.actor_id, a.first_name, a.last_name
       FROM actor a
       JOIN film_actor fa ON a.actor_id = fa.actor_id
       WHERE fa.film_id = $1
       ORDER BY a.last_name, a.first_name`,
      [id]
    );
    
    res.json({
      success: true,
      data: {
        ...result.rows[0],
        actors: actorsResult.rows
      }
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
    
    if (!title) {
      return res.status(400).json({
        success: false,
        message: 'El parámetro "title" es requerido'
      });
    }

    const result = await pool.query(
      `SELECT 
        f.film_id, 
        f.title, 
        f.description, 
        f.release_year, 
        f.rating,
        f.rental_rate,
        c.name as category,
        COUNT(DISTINCT i.inventory_id) as total_copies,
        COUNT(CASE WHEN r.return_date IS NULL THEN 1 END) as rented_copies
      FROM film f
      LEFT JOIN film_category fc ON f.film_id = fc.film_id
      LEFT JOIN category c ON fc.category_id = c.category_id
      LEFT JOIN inventory i ON f.film_id = i.film_id
      LEFT JOIN rental r ON i.inventory_id = r.inventory_id AND r.return_date IS NULL
      WHERE f.title ILIKE $1
      GROUP BY f.film_id, f.title, f.description, f.release_year, f.rating, f.rental_rate, c.name
      ORDER BY f.title`,
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
    const { limit = 20, offset = 0 } = req.query;

    const result = await pool.query(
      `SELECT 
        f.film_id, 
        f.title, 
        f.description, 
        f.release_year, 
        f.rating,
        f.rental_rate,
        c.name as category,
        COUNT(DISTINCT i.inventory_id) as total_copies
      FROM film f
      JOIN film_category fc ON f.film_id = fc.film_id
      JOIN category c ON fc.category_id = c.category_id
      LEFT JOIN inventory i ON f.film_id = i.film_id
      WHERE c.name ILIKE $1
      GROUP BY f.film_id, f.title, f.description, f.release_year, f.rating, f.rental_rate, c.name
      ORDER BY f.title
      LIMIT $2 OFFSET $3`,
      [category, limit, offset]
    );
    
    res.json({
      success: true,
      category: category,
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