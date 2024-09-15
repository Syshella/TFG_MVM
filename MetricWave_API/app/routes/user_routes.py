import smtplib
from urllib.parse import urljoin
from flask import Blueprint, request, jsonify, current_app
from app.models import User
from app import db, s
from flasgger.utils import swag_from
from email.message import EmailMessage
import ssl

user_blueprint = Blueprint('users', __name__)


@user_blueprint.route('/<int:user_id>', methods=['GET'])
@swag_from({
    'parameters': [
        {
            'name': 'id',
            'in': 'query',
            'type': 'integer',
            'required': True,
            'description': 'The user ID'
        }
    ],
    'responses': {
        200: {
            'description': 'A user object',
            'schema': {
                'id': 'User',
                'properties': {
                    'name': {
                        'type': 'string',
                        'description': 'The user\'s name'
                    },
                    'email': {
                        'type': 'string',
                        'description': 'The user\'s email'
                    }
                }
            }
        },
        404: {
            'description': 'User not found'
        }
    }
})
def get_user():
    user_id = request.args.get('id')
    user = User.query.get(user_id)
    if user is None:
        return jsonify({'error': 'User not found'}), 404
    return jsonify({'name': user.name, 'email': user.email})


@user_blueprint.route('/<int:user_id>', methods=['PUT'])
@swag_from({
    'parameters': [
        {
            'name': 'user_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'The user ID'
        },
        {
            'name': 'user',
            'in': 'body',
            'required': True,
            'schema': {
                'id': 'User',
                'properties': {
                    'name': {
                        'type': 'string'
                    },
                    'email': {
                        'type': 'string'
                    },
                    'password': {
                        'type': 'string'
                    }
                }
            }
        }
    ],
    'responses': {
        200: {
            'description': 'User updated successfully'
        },
        404: {
            'description': 'User not found'
        }
    }
})
def update_user(user_id):
    data = request.json
    user = User.query.get(user_id)
    if user is None:
        return jsonify({'error': 'User not found'}), 404
    user.name = data['name']
    user.email = data['email']
    user.set_hash_password(data['password'])
    db.session.commit()
    return jsonify({'message': 'User updated successfully'})


# @user_blueprint.route('/<int:user_id>', methods=['DELETE'])
# @swag_from({
#     'parameters': [
#         {
#             'name': 'user_id',
#             'in': 'path',
#             'type': 'integer',
#             'required': True,
#             'description': 'The user ID'
#         }
#     ],
#     'responses': {
#         200: {
#             'description': 'User deleted successfully'
#         },
#         404: {
#             'description': 'User not found'
#         }
#     }
# })
# def delete_user(user_id):
#     user = User.query.get(user_id)
#     if user is None:
#         return jsonify({'error': 'User not found'}), 404
#     db.session.delete(user)
#     db.session.commit()
#     return jsonify({'message': 'User deleted successfully'})


@user_blueprint.route('/login', methods=['POST'])
@swag_from({
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'email': {
                        'type': 'string',
                        'example': 'metricwavetfg@gmail.com'
                    },
                    'password': {
                        'type': 'string',
                        'example': 'metricwavetfg2024'
                    }
                }
            }
        }
    ],
    'responses': {
        200: {
            'description': 'Login successful',
            'schema': {
                'type': 'object',
                'properties': {
                    'message': {
                        'type': 'string',
                        'example': 'Login successful'
                    }
                }
            }
        },
        400: {
            'description': 'Missing email or password',
            'schema': {
                'type': 'object',
                'properties': {
                    'error': {
                        'type': 'string',
                        'example': 'Email and password are required'
                    }
                }
            }
        },
        401: {
            'description': 'Invalid credentials',
            'schema': {
                'type': 'object',
                'properties': {
                    'error': {
                        'type': 'string',
                        'example': 'Invalid credentials'
                    }
                }
            }
        },
        500: {
            'description': 'Internal server error',
            'schema': {
                'type': 'object',
                'properties': {
                    'error': {
                        'type': 'string',
                        'example': 'Internal server error'
                    }
                }
            }
        }
    }
})
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    user = User.query.filter_by(email=email).first()
    # print(f'Contrasena para {email} es {user.password}')

    if user is None or not user.check_hash_password(password):
        return jsonify({"error": "Invalid credentials"}), 401

    return jsonify({"message": "Login successful"}), 200


@user_blueprint.route('/register', methods=['POST'])
@swag_from({
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'email': {
                        'type': 'string',
                        'example': 'test@example.com'
                    },
                    'name': {
                        'type': 'string',
                        'example': 'Test User'
                    },
                    'password': {
                        'type': 'string',
                        'example': 'testpassword'
                    }
                }
            }
        }
    ],
    'responses': {
        201: {
            'description': 'User registered successfully',
            'schema': {
                'type': 'object',
                'properties': {
                    'message': {
                        'type': 'string',
                        'example': 'User registered successfully'
                    }
                }
            }
        },
        400: {
            'description': 'Missing or invalid parameters / User already exists',
            'schema': {
                'type': 'object',
                'properties': {
                    'error': {
                        'type': 'string',
                        'example': 'Email, name, and password are required'
                    }
                }
            }
        },
        500: {
            'description': 'Internal server error',
            'schema': {
                'type': 'object',
                'properties': {
                    'error': {
                        'type': 'string',
                        'example': 'Internal server error'
                    }
                }
            }
        }
    }
})
def create_user():
    data = request.get_json()
    email = data.get('email')
    name = data.get('name')
    password = data.get('password')

    if not email or not name or not password:
        return jsonify({"error": "Email, name, and password are required"}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"error": "User already exists"}), 400

    user = User(email=email, name=name)
    user.set_hash_password(password)  # Hashear la contraseña aquí
    db.session.add(user)
    db.session.commit()

    return jsonify({"message": "User registered successfully"}), 201


@user_blueprint.route('/forgot_password', methods=['POST'])
def forgot_password():
    if request.content_type == 'application/json':
        data = request.get_json()
    elif request.content_type == 'application/x-www-form-urlencoded':
        data = request.form
    else:
        return jsonify({"message": "Unsupported Media Type"}), 415

    email = data.get('email')
    user = User.query.filter_by(email=email).first()
    if user:
        token = s.dumps(user.email, salt='password-reset-salt')
        reset_url = urljoin('http://127.0.0.1:9000', f'reset/{token}')
        send_reset_email(user.email, reset_url)
    return jsonify({"message": "If your email exists within our database, you will receive an email shortly"}), 200


def send_reset_email(to_email, reset_url):
    em = EmailMessage()
    em['From'] = current_app.config['MAIL_DEFAULT_SENDER'][1]
    em['To'] = to_email
    em['Subject'] = 'Password Reset Request'
    em.set_content(
        f"To reset your password, visit the following link: {reset_url}\nIf you did not make this request then simply ignore this email and no changes will be made.")

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(current_app.config['MAIL_SERVER'], 465, context=context) as smtp:
        smtp.login(current_app.config['MAIL_USERNAME'], current_app.config['MAIL_PASSWORD'])
        smtp.sendmail(current_app.config['MAIL_DEFAULT_SENDER'], to_email, em.as_string())


@user_blueprint.route('/reset_password/<token>', methods=['POST'])
def reset_password(token):
    # print("Request Method:", request.method)
    # print("URL Accessed:", request.url)
    try:
        data = request.get_json()
        password = data.get('password')
        email = s.loads(token, salt='password-reset-salt', max_age=3600)
        user = User.query.filter_by(email=email).first()
        if user:
            user.set_hash_password(password)
            db.session.commit()
            return jsonify({"message": "Password reset successfully"}), 200
        else:
            return jsonify({"message": "User not found"}), 404
    except Exception as e:
        return jsonify({"message": "Invalid or expired token"}), 400
