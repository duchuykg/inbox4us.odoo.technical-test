from odoo import http
from odoo.http import request
from functools import wraps
import jwt
import json

SECRET_KEY = 'your_secret_key_here'
ALGORITHM = 'HS256'

def validate_request(*required_params):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Get the request data
            request_data = json.loads(request.httprequest.data)

            # Check if all required parameters are present
            for param in required_params:
                if param not in request_data:
                    return {'error': f'Missing required parameter: {param}'}, 400

            # Call the original function with the validated parameters
            return func(*args, **kwargs)
        return wrapper
    return decorator

def jwt_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
         # Get the 'Authorization' header from the request
        auth_header = request.httprequest.headers.get('Authorization')
        
        if not auth_header:
            return {'error': 'No token provided'}, 401
        
        # Extract the token from the Authorization header
        token = auth_header.split(' ')[1]
        
        try:
            decoded = jwt.decode(token, SECRET_KEY, ALGORITHM)
            if not decoded:
                return {'error': 'Invalid token'}, 401
        except jwt.ExpiredSignatureError:
            return {'error': 'Token has expired'}, 401
        except jwt.InvalidTokenError:
            return {'error': 'Invalid token'}, 401
        except Exception as e:
            return {'error': 'An error occurred while validating the token'}, 401

        return func(*args, **kwargs)
    return wrapper

class BookingController(http.Controller):

    @http.route('/api/bookings', type='json', auth='public', methods=['POST'])
    # @validate_request - TODO: handle request validation - Nice to have
    @validate_request('room_id', 'customer_id', 'checkin_date', 'checkout_date')
    # @jwt_required - TODO: handle jwt token in the request
    @jwt_required
    def create_booking(self, **kwargs):
        # TODO: need to handle authentication access token
        # TODO: Implement booking creation logic
        # Note: need to check availability of the room
        
        data = json.loads(request.httprequest.data)
        
        room_id = data['room_id']
        room = request.env['hotel.room'].sudo().search([('id', '=', room_id)], limit=1)
        if not room:
            return {'error': 'No room found with id: {}'.format(room_id)}, 401

        customer_id = data['customer_id']
        check_in_date = data['checkin_date']
        check_out_date = data['checkout_date']
        
        token = request.httprequest.headers.get('Authorization').split(' ')[1]
        decoded_token = jwt.decode(token, SECRET_KEY, ALGORITHM)
        user_id = decoded_token['user_id']
        
        user = request.env['res.users'].sudo().browse(user_id)
        
        customer = request.env['hotel.customer'].sudo().search([('email', '=', user.login)], limit=1)
        
        if not customer.id:
            return {'error': 'No customer found with name: {}'.format(user.name)}, 401
        if customer.id != customer_id:
            return {'error': 'Customer ID mismatch: expected {}, found {}'.format(customer_id, customer.id)}, 400
        
        if room.status == 'Maintenance' or room.status == 'maintenance':
            return {'error': 'Room {} is currently under maintenance'.format(room_id)}, 400
        else:
            is_available = self.check_room_availability(room_id, check_in_date, check_out_date)
            if not is_available: 
                return {'error': 'Room {} is not available for booking'.format(room_id)}, 400

            booking = request.env['hotel.booking'].sudo().create({
                'room_id': room_id,
                'customer_id': customer_id,
                'check_in_date': check_in_date,
                'check_out_date': check_out_date,
            })
            return {'message': 'Booking Room {} successful!'.format(room_id), 'total_amount': booking.total_amount}, 201

    def check_room_availability(self, room_id, check_in_date, check_out_date):
    # Check if the room is available for the selected time period.
        room = request.env['hotel.room'].sudo().browse(room_id)
        bookings = request.env['hotel.booking'].sudo().search([
            ('room_id', '=', room.id),
            ('check_in_date', '<=', check_out_date),
            ('check_out_date', '>=', check_in_date),
        ])
        if bookings:
            return False
        return True

    @http.route('/api/creating_room', type='json', auth='public', methods=['POST'])
    def create_room(self, **kwargs):
        # Get the request data
        data = json.loads(request.httprequest.data)

        # Extract the room id and name from the request data
        room = request.env['hotel.room'].sudo().create({
            'name': data.get('name'),
            'room_type': data.get('room_type'),
            'price_per_night': data.get('price_per_night'),
            'status': data.get('status')
        })

        return {
            'id': room.id,
            'name': room.name,
        }, 201
