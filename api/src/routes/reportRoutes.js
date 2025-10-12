const express = require('express');
const router = express.Router();
const reportController = require('../controllers/reportController');

// DVDs no devueltos
router.get('/unreturned-dvds', reportController.getUnreturnedDVDs);

// DVDs más rentados
router.get('/most-rented', reportController.getMostRentedDVDs);

// Ganancias por staff
router.get('/staff-revenue', reportController.getStaffRevenue);
router.get('/staff-revenue/:staff_id', reportController.getStaffRevenue);

module.exports = router;