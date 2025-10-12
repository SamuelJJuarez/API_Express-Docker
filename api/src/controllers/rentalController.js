const pool = require('../config/database');

// Crear una nueva renta
const createRental = async (req, res) => {
  const client = await pool.connect();
  
  try {
    const { customer_id, inventory_id, staff_id } = req.body;
    
    // Validar datos requeridos
    if (!customer_id || !inventory_id || !staff_id) {
      return res.status(400).json({
        success: false,
        message: 'customer_id, inventory_id y staff_id son requeridos'
      });
    }

    await client.query('BEGIN');

    // Verificar que el inventario existe y está disponible
    const inventoryCheck = await client.query(
      `SELECT i.inventory_id, f.title, f.rental_rate
       FROM inventory i
       JOIN film f ON i.film_id = f.film_id
       WHERE i.inventory_id = $1`,
      [inventory_id]
    );

    if (inventoryCheck.rows.length === 0) {
      await client.query('ROLLBACK');
      return res.status(404).json({
        success: false,
        message: 'Inventario no encontrado'
      });
    }

    // Verificar si el DVD ya está rentado (no devuelto)
    const rentalCheck = await client.query(
      'SELECT rental_id FROM rental WHERE inventory_id = $1 AND return_date IS NULL',
      [inventory_id]
    );

    if (rentalCheck.rows.length > 0) {
      await client.query('ROLLBACK');
      return res.status(400).json({
        success: false,
        message: 'Este DVD ya está rentado y no ha sido devuelto'
      });
    }

    // Verificar que el cliente existe
    const customerCheck = await client.query(
      'SELECT customer_id FROM customer WHERE customer_id = $1',
      [customer_id]
    );

    if (customerCheck.rows.length === 0) {
      await client.query('ROLLBACK');
      return res.status(404).json({
        success: false,
        message: 'Cliente no encontrado'
      });
    }

    // Verificar que el staff existe
    const staffCheck = await client.query(
      'SELECT staff_id FROM staff WHERE staff_id = $1',
      [staff_id]
    );

    if (staffCheck.rows.length === 0) {
      await client.query('ROLLBACK');
      return res.status(404).json({
        success: false,
        message: 'Staff no encontrado'
      });
    }

    // Crear la renta
    const rentalResult = await client.query(
      `INSERT INTO rental (rental_date, inventory_id, customer_id, staff_id, last_update)
       VALUES (NOW(), $1, $2, $3, NOW())
       RETURNING rental_id, rental_date`,
      [inventory_id, customer_id, staff_id]
    );

    const rental = rentalResult.rows[0];

    await client.query('COMMIT');

    res.status(201).json({
      success: true,
      message: 'Renta creada exitosamente',
      data: {
        rental_id: rental.rental_id,
        rental_date: rental.rental_date,
        film_title: inventoryCheck.rows[0].title,
        rental_rate: inventoryCheck.rows[0].rental_rate,
        customer_id,
        inventory_id,
        staff_id
      }
    });

  } catch (error) {
    await client.query('ROLLBACK');
    console.error('Error al crear renta:', error);
    res.status(500).json({
      success: false,
      message: 'Error al crear la renta',
      error: error.message
    });
  } finally {
    client.release();
  }
};

// Realizar devolución
const returnRental = async (req, res) => {
  const client = await pool.connect();
  
  try {
    const { rental_id } = req.params;
    
    await client.query('BEGIN');

    // Verificar que la renta existe y no ha sido devuelta
    const rentalCheck = await client.query(
      `SELECT r.rental_id, r.rental_date, r.customer_id, r.inventory_id,
              f.title, f.rental_rate, f.rental_duration
       FROM rental r
       JOIN inventory i ON r.inventory_id = i.inventory_id
       JOIN film f ON i.film_id = f.film_id
       WHERE r.rental_id = $1`,
      [rental_id]
    );

    if (rentalCheck.rows.length === 0) {
      await client.query('ROLLBACK');
      return res.status(404).json({
        success: false,
        message: 'Renta no encontrada'
      });
    }

    const rental = rentalCheck.rows[0];

    // Verificar si ya fue devuelta
    const returnCheck = await client.query(
      'SELECT return_date FROM rental WHERE rental_id = $1',
      [rental_id]
    );

    if (returnCheck.rows[0].return_date !== null) {
      await client.query('ROLLBACK');
      return res.status(400).json({
        success: false,
        message: 'Esta renta ya fue devuelta',
        return_date: returnCheck.rows[0].return_date
      });
    }

    // Actualizar la fecha de devolución
    const returnResult = await client.query(
      `UPDATE rental 
       SET return_date = NOW(), last_update = NOW()
       WHERE rental_id = $1
       RETURNING return_date`,
      [rental_id]
    );

    // Calcular días de renta y costo
    const returnDate = returnResult.rows[0].return_date;
    const rentalDate = rental.rental_date;
    const daysRented = Math.ceil((returnDate - rentalDate) / (1000 * 60 * 60 * 24));
    const totalAmount = (rental.rental_rate * daysRented).toFixed(2);

    // Crear el pago
    const paymentResult = await client.query(
      `INSERT INTO payment (customer_id, staff_id, rental_id, amount, payment_date)
       SELECT customer_id, staff_id, $1, $2, NOW()
       FROM rental
       WHERE rental_id = $1
       RETURNING payment_id, amount`,
      [rental_id, totalAmount]
    );

    await client.query('COMMIT');

    res.json({
      success: true,
      message: 'Devolución procesada exitosamente',
      data: {
        rental_id: parseInt(rental_id),
        film_title: rental.title,
        rental_date: rentalDate,
        return_date: returnDate,
        days_rented: daysRented,
        rental_rate: rental.rental_rate,
        total_amount: parseFloat(totalAmount),
        payment_id: paymentResult.rows[0].payment_id
      }
    });

  } catch (error) {
    await client.query('ROLLBACK');
    console.error('Error al procesar devolución:', error);
    res.status(500).json({
      success: false,
      message: 'Error al procesar la devolución',
      error: error.message
    });
  } finally {
    client.release();
  }
};

// Cancelar renta (solo si no ha sido devuelta)
const cancelRental = async (req, res) => {
  const client = await pool.connect();
  
  try {
    const { rental_id } = req.params;
    
    await client.query('BEGIN');

    // Verificar que la renta existe
    const rentalCheck = await client.query(
      `SELECT r.rental_id, r.return_date, f.title
       FROM rental r
       JOIN inventory i ON r.inventory_id = i.inventory_id
       JOIN film f ON i.film_id = f.film_id
       WHERE r.rental_id = $1`,
      [rental_id]
    );

    if (rentalCheck.rows.length === 0) {
      await client.query('ROLLBACK');
      return res.status(404).json({
        success: false,
        message: 'Renta no encontrada'
      });
    }

    const rental = rentalCheck.rows[0];

    if (rental.return_date !== null) {
      await client.query('ROLLBACK');
      return res.status(400).json({
        success: false,
        message: 'No se puede cancelar una renta que ya fue devuelta'
      });
    }

    // Eliminar la renta
    await client.query(
      'DELETE FROM rental WHERE rental_id = $1',
      [rental_id]
    );

    await client.query('COMMIT');

    res.json({
      success: true,
      message: 'Renta cancelada exitosamente',
      data: {
        rental_id: parseInt(rental_id),
        film_title: rental.title
      }
    });

  } catch (error) {
    await client.query('ROLLBACK');
    console.error('Error al cancelar renta:', error);
    res.status(500).json({
      success: false,
      message: 'Error al cancelar la renta',
      error: error.message
    });
  } finally {
    client.release();
  }
};

// Obtener todas las rentas de un cliente
const getCustomerRentals = async (req, res) => {
  try {
    const { customer_id } = req.params;
    const { status } = req.query; // 'active', 'returned', 'all'

    let query = `
      SELECT 
        r.rental_id,
        r.rental_date,
        r.return_date,
        f.title,
        f.rental_rate,
        c.name as category,
        CASE 
          WHEN r.return_date IS NULL THEN 'Activa'
          ELSE 'Devuelta'
        END as status,
        CASE 
          WHEN r.return_date IS NULL 
          THEN EXTRACT(DAY FROM (NOW() - r.rental_date))
          ELSE EXTRACT(DAY FROM (r.return_date - r.rental_date))
        END as days_rented
      FROM rental r
      JOIN inventory i ON r.inventory_id = i.inventory_id
      JOIN film f ON i.film_id = f.film_id
      LEFT JOIN film_category fc ON f.film_id = fc.film_id
      LEFT JOIN category c ON fc.category_id = c.category_id
      WHERE r.customer_id = $1
    `;

    if (status === 'active') {
      query += ' AND r.return_date IS NULL';
    } else if (status === 'returned') {
      query += ' AND r.return_date IS NOT NULL';
    }

    query += ' ORDER BY r.rental_date DESC';

    const result = await pool.query(query, [customer_id]);

    // Obtener información del cliente
    const customerInfo = await pool.query(
      `SELECT customer_id, first_name, last_name, email
       FROM customer
       WHERE customer_id = $1`,
      [customer_id]
    );

    if (customerInfo.rows.length === 0) {
      return res.status(404).json({
        success: false,
        message: 'Cliente no encontrado'
      });
    }

    res.json({
      success: true,
      customer: customerInfo.rows[0],
      total_rentals: result.rows.length,
      rentals: result.rows
    });

  } catch (error) {
    console.error('Error al obtener rentas del cliente:', error);
    res.status(500).json({
      success: false,
      message: 'Error al obtener las rentas del cliente',
      error: error.message
    });
  }
};

module.exports = {
  createRental,
  returnRental,
  cancelRental,
  getCustomerRentals
};