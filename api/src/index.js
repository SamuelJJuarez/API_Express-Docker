const express = require('express');
const cors = require('cors');
require('dotenv').config();

const filmRoutes = require('./routes/filmRoutes');
const rentalRoutes = require('./routes/rentalRoutes');
const reportRoutes = require('./routes/reportRoutes');
const customerRoutes = require('./routes/customerRoutes');
const staffRoutes = require('./routes/staffRoutes');

const app = express();
const PORT = process.env.PORT || 3000;

// Middlewares
app.use(cors());
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Ruta de prueba
app.get('/', (req, res) => {
  res.json({
    message: 'Bienvenido a la API de DVD Rental',
    version: '2.0.0',
    endpoints: {
      films: {
        getAll: 'GET /films',
        getById: 'GET /films/:id',
        search: 'GET /films/search?title=palabra',
        byCategory: 'GET /films/category/:category'
      },
      customers: {
        getAll: 'GET /api/customers',
        getById: 'GET /api/customers/:id'
      },
      staff: {
        getAll: 'GET /api/staff',
        getById: 'GET /api/staff/:id'
      },
      rentals: {
        getAll: 'GET /rentals',
        create: 'POST /rentals',
        return: 'PUT /rentals/:rental_id/return',
        cancel: 'DELETE /rentals/:rental_id',
        customerRentals: 'GET /rentals/customer/:customer_id'
      },
      reports: {
        unreturnedDVDs: 'GET /reports/unreturned-dvds',
        mostRented: 'GET /reports/most-rented?limit=10',
        staffRevenue: 'GET /reports/staff-revenue',
        staffRevenueById: 'GET /reports/staff-revenue/:staff_id'
      }
    }
  });
});

// Rutas
app.use('/films', filmRoutes);
app.use('/rentals', rentalRoutes);
app.use('/customers', customerRoutes);
app.use('/staff', staffRoutes);
app.use('/reports', reportRoutes);

// Manejo de rutas no encontradas
app.use((req, res) => {
  res.status(404).json({
    success: false,
    message: 'Ruta no encontrada'
  });
});

// Manejo de errores
app.use((err, req, res, next) => {
  console.error(err.stack);
  res.status(500).json({
    success: false,
    message: 'Error interno del servidor',
    error: err.message
  });
});

// Iniciar servidor
app.listen(PORT, () => {
  console.log(`Servidor corriendo en http://localhost:${PORT}`);
});