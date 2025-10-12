const express = require('express');
const router = express.Router();
const rentalController = require('../controllers/rentalController');

// Obtener todas las rentas
router.get('/', rentalController.getAllRentals);

// Obtener rentas de un cliente específico
router.get('/customer/:customer_id', rentalController.getCustomerRentals);

// Crear renta
router.post('/', rentalController.createRental);

// Realizar devolución
router.put('/:rental_id/return', rentalController.returnRental);

// Cancelar renta
router.delete('/:rental_id', rentalController.cancelRental);

module.exports = router;