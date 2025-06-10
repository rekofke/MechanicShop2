from jose import JWTError, jwt
import jose
from datetime import datetime, timedelta, timezone
from functools import wraps
from flask import request, jsonify
import os

SECRET_KEY = os.environ.get('SECRET_KEY') or "super secret secrets"

def encode_token(user_id, role='user'):
    payload = {
        'exp': datetime.now(timezone.utc) + timedelta(days=1), # expiration time set to 1 day
        'iat': datetime.now(timezone.utc), # issuad at time
        'sub': str(user_id), #* user_id must be string in order to decode properly
        'role': role  #* role can be 'user' or 'mechanic'
    }

    token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
    return token


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        # Check if token is passed in the headers
        if 'Authorization' in request.headers:
            # headers dictionary in rewuests, authorization key
            token = request.headers['Authorization'].split()[1]

        if not token:
            return jsonify({'error': 'Token is missing!'}), 401
        
        try:
            data = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            user_id = data['sub']
            request.user_id = user_id

        except jose.exceptions.ExpiredSignatureError:
            return jsonify({'error': 'Token has expired!'}), 401
        except jose.exceptions.JWTError:
            return jsonify({'error': 'Invalid token!'}), 401
        
        return f(*args, **kwargs)
    
    return decorated

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        # Check if token is passed in the headers
        if 'Authorization' in request.headers:
            # headers dictionary in rewuests, authorization key
            token = request.headers['Authorization'].split()[1]

        if not token:
            return jsonify({'error': 'Token is missing!'}), 401
        
        try:
            data = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            user_id = data['sub']
            request.user_id = user_id
            if not data['role'] == 'mechanic':
                return jsonify({'error': 'Admin privileges required!'}), 403

        except jose.exceptions.ExpiredSignatureError:
            return jsonify({'error': 'Token has expired!'}), 401
        except jose.exceptions.JWTError:
            return jsonify({'error': 'Invalid token!'}), 401
        
        return f(*args, **kwargs)
    
    return decorated