const express = require('express');
const router = express.Router();
const customerController = require('../controllers/customerController');

// Obtener todos los clientes
router.get('/', customerController.getAllCustomers);

// Obtener un cliente por ID
router.get('/:id', customerController.getCustomerById);

module.exports = router;