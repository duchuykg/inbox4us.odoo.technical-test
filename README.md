## Inbox4us - Technical Test Requirements for Odoo Hotel Booking Module
### Overview
- Odoo version 17.0
- Postman collection for testing the API: [Postman collection](https://github.com/duchuykg/inbox4us.odoo.technical-test/blob/main/Odoo17.postman_collection.json)
- Document Each Function: Provide documentation for each function, explaining its purpose, parameters, and return values.
[API Document](https://documenter.getpostman.com/view/26645840/2sA3QwcA8g)

### Instructions
- Fork the Repository: Fork the provided repository to your personal GitHub account.
- Clone the Repository: Clone the forked repository to your local development environment.
- Implement the Features: Complete the following tasks in your local repository.
- Commit and Push: Commit your changes and push them to your forked repository.

### Requirements
#### 1. Write REST API for Authentication using JWT
Implement user registration and login endpoints.
Use JWT for token-based authentication.

```
File: controllers/auth_controller.py
```

- Register
```bash
curl -X POST http://localhost:8069/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "email": "john@inbox4us.xyz",
    "password": "password"
    }'
```

- Login 
```bash
curl -X POST http://localhost:8069/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
        "email": "john@inbox4us.xyz",
        "password": "password"
    }'
```

#### 2. Write API for Making a Booking
Implement an endpoint to create a new booking.
```
File: controllers/booking_controller.py
```

- Create Booking
```bash
curl -X POST http://localhost:8069/api/booking \
  -H "Content-Type: application/json
  --header 'Authorization: Bearer <REPLACE_ACCESSTOKEN>' \
  -d '{
    "room_id": 1,
    "customer_id": 1,
    "checkin_date": "2022-01-01",
    "checkout_date": "2022-01-05"
  }'
```

#### 3. Nice to Have (Optional)
- Handle Booking Status: Implement logic to manage booking statuses (checkin, checkout, booked).
- Adding Validation for Parameters Using Decorators: Implement parameter validation using decorators to ensure correct data is provided in the API requests.
- Write postman collection for testing the API.
- Apply Best Practices: Write clean, maintainable code following industry best practices.
- Document Each Function: Provide documentation for each function, explaining its purpose, parameters, and return values.