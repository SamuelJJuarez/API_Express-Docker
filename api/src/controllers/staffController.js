const pool = require('../config/database');

// Obtener todos los miembros del staff
const getAllStaff = async (req, res) => {
  try {
    const { active, store_id } = req.query;

    let query = `
      SELECT 
        s.staff_id,
        s.first_name,
        s.last_name,
        s.email,
        s.active,
        s.username,
        s.store_id,
        a.address,
        a.district,
        a.phone,
        ci.city,
        co.country,
        COUNT(DISTINCT r.rental_id) as total_rentals,
        COALESCE(SUM(p.amount), 0) as total_revenue
      FROM staff s
      JOIN address a ON s.address_id = a.address_id
      JOIN city ci ON a.city_id = ci.city_id
      JOIN country co ON ci.country_id = co.country_id
      LEFT JOIN rental r ON s.staff_id = r.staff_id
      LEFT JOIN payment p ON r.rental_id = p.rental_id
    `;

    const params = [];
    const conditions = [];

    if (active !== undefined) {
      conditions.push(`s.active = $${params.length + 1}`);
      params.push(active === 'true');
    }

    if (store_id) {
      conditions.push(`s.store_id = $${params.length + 1}`);
      params.push(store_id);
    }

    if (conditions.length > 0) {
      query += ' WHERE ' + conditions.join(' AND ');
    }

    query += `
      GROUP BY s.staff_id, s.first_name, s.last_name, s.email, 
               s.active, s.username, s.store_id, a.address, 
               a.district, a.phone, ci.city, co.country
      ORDER BY s.staff_id
    `;

    const result = await pool.query(query, params);

    res.json({
      success: true,
      count: result.rows.length,
      data: result.rows
    });

  } catch (error) {
    console.error('Error al obtener staff:', error);
    res.status(500).json({
      success: false,
      message: 'Error al obtener el staff',
      error: error.message
    });
  }
};

// Obtener un miembro del staff por ID
const getStaffById = async (req, res) => {
  try {
    const { id } = req.params;

    const result = await pool.query(
      `SELECT 
        s.staff_id,
        s.first_name,
        s.last_name,
        s.email,
        s.active,
        s.username,
        s.store_id,
        a.address,
        a.address2,
        a.district,
        a.postal_code,
        a.phone,
        ci.city,
        co.country,
        COUNT(DISTINCT r.rental_id) as total_rentals,
        COUNT(DISTINCT p.payment_id) as total_payments,
        COALESCE(SUM(p.amount), 0) as total_revenue
      FROM staff s
      JOIN address a ON s.address_id = a.address_id
      JOIN city ci ON a.city_id = ci.city_id
      JOIN country co ON ci.country_id = co.country_id
      LEFT JOIN rental r ON s.staff_id = r.staff_id
      LEFT JOIN payment p ON r.rental_id = p.rental_id
      WHERE s.staff_id = $1
      GROUP BY s.staff_id, s.first_name, s.last_name, s.email, 
               s.active, s.username, s.store_id, a.address, a.address2,
               a.district, a.postal_code, a.phone, ci.city, co.country`,
      [id]
    );

    if (result.rows.length === 0) {
      return res.status(404).json({
        success: false,
        message: 'Miembro del staff no encontrado'
      });
    }

    res.json({
      success: true,
      data: result.rows[0]
    });

  } catch (error) {
    console.error('Error al obtener miembro del staff:', error);
    res.status(500).json({
      success: false,
      message: 'Error al obtener el miembro del staff',
      error: error.message
    });
  }
};

module.exports = {
  getAllStaff,
  getStaffById
};