const express = require('express');
const router = express.Router();
const reportController = require('../controllers/reportController');
const rentalController = require('../controllers/rentalController');

// DVDs no devueltos
router.get('/unreturned-dvds', reportController.getUnreturnedDVDs);

// DVDs más rentados
router.get('/most-rented', reportController.getMostRentedDVDs);

// Ganancias por staff
router.get('/staff-revenue', reportController.getStaffRevenue);
router.get('/staff-revenue/:staff_id', reportController.getStaffRevenue);

// Rentas de un cliente específico
router.get('/customer-rentals/:customer_id', rentalController.getCustomerRentals);

module.exports = router;