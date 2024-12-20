from flask import Blueprint, jsonify, request
from application.models import User
from functools import wraps
from flask_jwt_extended import create_access_token, set_access_cookies, unset_jwt_cookies, verify_jwt_in_request, get_jwt
from application.extensions import bcrypt

auth_bp = Blueprint('auth',__name__)

def role_required(roles):
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            for role in roles:
                if claims["role"]==role:
                    return fn(*args, **kwargs)
            else:
                return jsonify({"message": "Unauthorized role"}), 403
        return decorator
    return wrapper

@auth_bp.post('/login')
def login():
    
    email = request.json.get("email", None)
    password = request.json.get("password", None)

    if not email:
        return jsonify({"message":"Email not provided"}), 400
    if not password:
        return jsonify({"message":"Password not provided"}), 400

    user = User.query.filter_by(email=email).first()

    if not user:
        return jsonify({"message":"User does not exist"}), 404
    if not (bcrypt.check_password_hash(user.password, password)):
        return jsonify({"message":"Incorrect password"}), 400
    
    if user.professional:
        if user.professional.flag == True:
            return jsonify({"message":"Professional is flagged by admin. So can't login."}), 400
        if user.professional.status == 'unapproved':
            return jsonify({"message":"Professional is not approved by admin. So could not login."}), 400
        
    if user.customer:
        if user.customer.flag == True:
            return jsonify({"message":"Customer is flagged by admin. So could not login."}), 400
    
    access_token = create_access_token(identity=user.id)

    response = jsonify(
        {
            "access_token":access_token,
            "message":"Login Successful",
            "role":user.role,
            "user_id":user.id
        }
    )
    set_access_cookies(response, access_token)

    return response, 200

@auth_bp.get('/logout')
def logout():
    response = jsonify({"message": "Logout Successful"})
    unset_jwt_cookies(response)
    return response


    
    