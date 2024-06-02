from odoo import http
from odoo.http import request
import jwt
import json
import datetime
from functools import wraps

SECRET_KEY = 'your_secret_key_here'
ALGORITHM = 'HS256'
TOKEN_EXPIRATION_MINUTES = 24 * 60 # Token expires in 1 day

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
class AuthController(http.Controller):

    @http.route('/api/auth/register', type='json', auth="none", methods=['POST'], cors='*', csrf=False)
    @validate_request('name', 'email', 'password')
    def register(self, **kwargs):
        # TODO: Implement user registration logic
        # Get the data from the HTTP request
        byte_string = request.httprequest.data
        data = json.loads(byte_string.decode('utf-8'))
        
        name = data['name']
        email = data['email']
        password = data['password']
        
        # Check if any of the required fields are missing
        if not name or not email or not password:
            return {'error': 'Missing required fields'}, 400

        # Check if a user with the provided email already exists in the system
        existing_user = http.request.env['res.users'].sudo().search([('login', '=', email)], limit=1)
        if existing_user:
            return {'error': 'User already exists!'}, 400

        # Create a new user with the provided details
        companies = http.request.env['res.company'].sudo().search([], limit=1)
        new_user = http.request.env['res.users'].sudo().create({
            'name': name,
            'login': email,
            'password': password,
            'company_id': companies[0].id,
            'company_ids': [(6, 0, [companies[0].id])],
        })
        
        # Create a new hotel customer with the provided details
        hotel_customer = http.request.env['hotel.customer'].sudo().create({
            'name': name,
            'email': email,
            'phone': 0,
        })

        return {'message': 'Registration successful!'}, 201

    @http.route('/api/auth/login', type='json', auth='none', methods=['POST'], cors='*', csrf=False)
    @validate_request('email', 'password')

    def login(self, **kwargs):
        # TODO: Implement user login logic and return JWT token
         # Get the data from the HTTP request
        byte_string = request.httprequest.data
        data = json.loads(byte_string.decode('utf-8'))
        
        email = data['email']
        password = data['password']
        
        # Attempt to authenticate the user using request.session.authenticate()
        try:
            user_id = request.session.authenticate(request.db, email, password)
        except Exception as e:
            return {'error': str(e)}, 401
                
        # Generate a JWT token for the authenticated user
        now = datetime.datetime.now()
        expiration = now + datetime.timedelta(minutes=TOKEN_EXPIRATION_MINUTES)
        payload = {
            'user_id': user_id,
            'exp': int(expiration.timestamp())
        }
        token = jwt.encode(payload, SECRET_KEY, ALGORITHM)
        
        return {'token': token, 'message': 'Login successful'}, 200


        
