const express = require('express');
const router = express.Router();
const rentalController = require('../controllers/rentalController');

// Crear renta
router.post('/', rentalController.createRental);

// Realizar devolución
router.put('/:rental_id/return', rentalController.returnRental);

// Cancelar renta
router.delete('/:rental_id', rentalController.cancelRental);

// Obtener rentas de un cliente
router.get('/customer/:customer_id', rentalController.getCustomerRentals);

module.exports = router;