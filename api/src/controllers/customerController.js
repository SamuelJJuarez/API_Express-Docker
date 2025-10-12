const pool = require('../config/database');

// Obtener todos los clientes
const getAllCustomers = async (req, res) => {
  try {
    const { active, store_id, limit = 50, offset = 0 } = req.query;

    let query = `
      SELECT 
        c.customer_id,
        c.first_name,
        c.last_name,
        c.email,
        c.active,
        c.create_date,
        a.address,
        a.district,
        ci.city,
        co.country,
        s.store_id,
        COUNT(DISTINCT r.rental_id) as total_rentals,
        COUNT(CASE WHEN r.return_date IS NULL THEN 1 END) as active_rentals
      FROM customer c
      JOIN address a ON c.address_id = a.address_id
      JOIN city ci ON a.city_id = ci.city_id
      JOIN country co ON ci.country_id = co.country_id
      JOIN store s ON c.store_id = s.store_id
      LEFT JOIN rental r ON c.customer_id = r.customer_id
    `;

    const params = [];
    const conditions = [];

    if (active !== undefined) {
      conditions.push(`c.active = $${params.length + 1}`);
      params.push(active === 'true' ? 1 : 0);
    }

    if (store_id) {
      conditions.push(`c.store_id = $${params.length + 1}`);
      params.push(store_id);
    }

    if (conditions.length > 0) {
      query += ' WHERE ' + conditions.join(' AND ');
    }

    query += `
      GROUP BY c.customer_id, c.first_name, c.last_name, c.email, 
               c.active, c.create_date, a.address, a.district, 
               ci.city, co.country, s.store_id
      ORDER BY c.customer_id
      LIMIT $${params.length + 1} OFFSET $${params.length + 2}
    `;

    params.push(limit, offset);

    const result = await pool.query(query, params);

    // Obtener el total de clientes
    const countQuery = `
      SELECT COUNT(*) as total
      FROM customer c
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
    console.error('Error al obtener clientes:', error);
    res.status(500).json({
      success: false,
      message: 'Error al obtener los clientes',
      error: error.message
    });
  }
};

// Obtener un cliente por ID
const getCustomerById = async (req, res) => {
  try {
    const { id } = req.params;

    const result = await pool.query(
      `SELECT 
        c.customer_id,
        c.first_name,
        c.last_name,
        c.email,
        c.active,
        c.create_date,
        a.address,
        a.address2,
        a.district,
        a.postal_code,
        a.phone,
        ci.city,
        co.country,
        s.store_id,
        COUNT(DISTINCT r.rental_id) as total_rentals,
        COUNT(CASE WHEN r.return_date IS NULL THEN 1 END) as active_rentals,
        COALESCE(SUM(p.amount), 0) as total_spent
      FROM customer c
      JOIN address a ON c.address_id = a.address_id
      JOIN city ci ON a.city_id = ci.city_id
      JOIN country co ON ci.country_id = co.country_id
      JOIN store s ON c.store_id = s.store_id
      LEFT JOIN rental r ON c.customer_id = r.customer_id
      LEFT JOIN payment p ON r.rental_id = p.rental_id
      WHERE c.customer_id = $1
      GROUP BY c.customer_id, c.first_name, c.last_name, c.email, 
               c.active, c.create_date, a.address, a.address2, a.district,
               a.postal_code, a.phone, ci.city, co.country, s.store_id`,
      [id]
    );

    if (result.rows.length === 0) {
      return res.status(404).json({
        success: false,
        message: 'Cliente no encontrado'
      });
    }

    res.json({
      success: true,
      data: result.rows[0]
    });

  } catch (error) {
    console.error('Error al obtener cliente:', error);
    res.status(500).json({
      success: false,
      message: 'Error al obtener el cliente',
      error: error.message
    });
  }
};

module.exports = {
  getAllCustomers,
  getCustomerById
};