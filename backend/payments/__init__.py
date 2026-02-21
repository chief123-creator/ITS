# Payment Module Blueprint
# This module handles all payment-related operations for the Traffic Reward System

from flask import Blueprint

# Create the payments blueprint
payments_bp = Blueprint('payments', __name__, url_prefix='/payments')

# Import routes to register them with the blueprint
# These imports must happen after blueprint creation
from payments.routes import payments_routes, withdraw_routes, payment_methods_routes, notification_routes
