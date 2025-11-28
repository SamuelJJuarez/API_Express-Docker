const pool = require('../config/database');

// Identificar DVDs que no se han devuelto
const getUnreturnedDVDs = async (req, res) => {
  try {
    const result = await pool.query(
      `SELECT 
        r.rental_id,
        r.rental_date,
        EXTRACT(DAY FROM (NOW() - r.rental_date)) as days_rented,
        f.film_id,
        f.title,
        f.rental_duration as expected_duration,
        c.customer_id,
        c.first_name || ' ' || c.last_name as customer_name,
        c.email,
        s.first_name || ' ' || s.last_name as staff_name,
        CASE 
          WHEN EXTRACT(DAY FROM (NOW() - r.rental_date)) > f.rental_duration 
          THEN 'Atrasado'
          ELSE 'En tiempo'
        END as status
      FROM rental r
      JOIN inventory i ON r.inventory_id = i.inventory_id
      JOIN film f ON i.film_id = f.film_id
      JOIN customer c ON r.customer_id = c.customer_id
      JOIN staff s ON r.staff_id = s.staff_id
      WHERE r.return_date IS NULL
      ORDER BY r.rental_date ASC`
    );

    const late = result.rows.filter(r => r.status === 'Atrasado');
    const onTime = result.rows.filter(r => r.status === 'En tiempo');

    res.json({
      success: true,
      summary: {
        total_unreturned: result.rows.length,
        late_returns: late.length,
        on_time: onTime.length
      },
      data: result.rows
    });

  } catch (error) {
    console.error('Error al obtener DVDs no devueltos:', error);
    res.status(500).json({
      success: false,
      message: 'Error al obtener DVDs no devueltos',
      error: error.message
    });
  }
};

// Determinar los DVDs más rentados
const getMostRentedDVDs = async (req, res) => {
  try {
    const { limit = 10 } = req.query;

    const result = await pool.query(
      `SELECT 
        f.film_id,
        f.title,
        f.rental_rate,
        f.release_year,
        f.rating,
        c.name as category,
        COUNT(r.rental_id) as total_rentals,
        COUNT(CASE WHEN r.return_date IS NOT NULL THEN 1 END) as completed_rentals,
        COUNT(CASE WHEN r.return_date IS NULL THEN 1 END) as active_rentals,
        COALESCE(SUM(p.amount), 0) as total_revenue,
        MAX(r.rental_date) as last_rental_date
      FROM film f
      INNER JOIN inventory i ON f.film_id = i.film_id
      INNER JOIN rental r ON i.inventory_id = r.inventory_id
      LEFT JOIN payment p ON r.rental_id = p.rental_id
      LEFT JOIN film_category fc ON f.film_id = fc.film_id
      LEFT JOIN category c ON fc.category_id = c.category_id
      GROUP BY f.film_id, f.title, f.rental_rate, f.release_year, f.rating, c.name
      ORDER BY total_rentals DESC
      LIMIT $1`,
      [limit]
    );

    res.json({
      success: true,
      generated_at: new Date().toISOString(),
      count: result.rows.length,
      data: result.rows
    });

  } catch (error) {
    console.error('Error al obtener DVDs más rentados:', error);
    res.status(500).json({
      success: false,
      message: 'Error al obtener DVDs más rentados',
      error: error.message
    });
  }
};

// Calcular total de ganancias por staff
const getStaffRevenue = async (req, res) => {
  try {
    const { staff_id } = req.params;
    const { start_date, end_date } = req.query;

    console.log('📊 Calculando ganancias del staff:', { staff_id, start_date, end_date });

    let query = `
      SELECT 
        s.staff_id,
        s.first_name,
        s.last_name,
        s.first_name || ' ' || s.last_name as staff_name,
        s.email,
        st.store_id,
        COUNT(DISTINCT r.rental_id) FILTER (WHERE r.rental_id IS NOT NULL) as total_rentals,
        COUNT(DISTINCT p.payment_id) FILTER (WHERE p.payment_id IS NOT NULL) as total_payments,
        COALESCE(SUM(p.amount), 0) as total_revenue,
        COALESCE(AVG(p.amount), 0) as average_payment,
        MIN(p.payment_date) as first_payment_date,
        MAX(p.payment_date) as last_payment_date
      FROM staff s
      JOIN store st ON s.store_id = st.store_id
      LEFT JOIN rental r ON s.staff_id = r.staff_id
      LEFT JOIN payment p ON r.rental_id = p.rental_id
    `;

    const params = [];
    const conditions = [];

    if (staff_id) {
      conditions.push(`s.staff_id = $${params.length + 1}`);
      params.push(staff_id);
    }

    if (start_date) {
      conditions.push(`p.payment_date >= $${params.length + 1}`);
      params.push(start_date);
    }

    if (end_date) {
      conditions.push(`p.payment_date <= $${params.length + 1}`);
      params.push(end_date);
    }

    if (conditions.length > 0) {
      query += ' WHERE ' + conditions.join(' AND ');
    }

    query += ` GROUP BY s.staff_id, s.first_name, s.last_name, s.email, st.store_id
               ORDER BY total_revenue DESC`;

    const result = await pool.query(query, params);

    if (staff_id && result.rows.length === 0) {
      return res.status(404).json({
        success: false,
        message: 'Staff no encontrado'
      });
    }

    // Si es un staff específico, agregar detalles adicionales
    if (staff_id) {
      const detailQuery = `
        SELECT 
          DATE(p.payment_date) as payment_date,
          COUNT(p.payment_id) as payments_count,
          SUM(p.amount) as daily_revenue
        FROM payment p
        JOIN rental r ON p.rental_id = r.rental_id
        WHERE r.staff_id = $1
        ${start_date ? `AND p.payment_date >= $2` : ''}
        ${end_date ? `AND p.payment_date <= $${start_date ? '3' : '2'}` : ''}
        GROUP BY DATE(p.payment_date)
        ORDER BY payment_date DESC
        LIMIT 30
      `;

      const detailParams = [staff_id];
      if (start_date) detailParams.push(start_date);
      if (end_date) detailParams.push(end_date);

      const detailResult = await pool.query(detailQuery, detailParams);

      return res.json({
        success: true,
        staff_info: result.rows[0],
        daily_breakdown: detailResult.rows
      });
    }

    res.json({
      success: true,
      count: result.rows.length,
      total_revenue_all_staff: result.rows.reduce((sum, row) => sum + parseFloat(row.total_revenue || 0), 0),
      data: result.rows
    });

  } catch (error) {
    console.error('Error al calcular ganancias del staff:', error);
    res.status(500).json({
      success: false,
      message: 'Error al calcular ganancias del staff',
      error: error.message
    });
  }
};

module.exports = {
  getUnreturnedDVDs,
  getMostRentedDVDs,
  getStaffRevenue
};