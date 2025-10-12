const express = require('express');
const router = express.Router();
const staffController = require('../controllers/staffController');

// Obtener todos los miembros del staff
router.get('/', staffController.getAllStaff);

// Obtener un miembro del staff por ID
router.get('/:id', staffController.getStaffById);

module.exports = router;