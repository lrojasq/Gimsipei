from flask import Blueprint, request,json, jsonify, current_app, render_template, redirect, url_for, flash, make_response
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, set_access_cookies, unset_jwt_cookies
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
from src.models.user import User, UserRole
from src.database.database import SessionLocal
from typing import Dict, Any, Union
from functools import wraps

bp = Blueprint('auth', __name__, url_prefix='/auth/', template_folder='templates')

def login_required(f):
    @wraps(f)
    @jwt_required()
    def decorated_function(*args, **kwargs):
        user_id = get_jwt_identity()
        if not user_id:
            flash('Por favor inicie sesión para acceder a esta página.', 'warning')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function



@bp.route('/login', methods=['GET', 'POST'])
def login() -> Union[str, tuple[Dict[str, Any], int]]:

    if request.method == 'GET':
        return render_template('login.html')
        
    if request.is_json:
        data = request.get_json()
    else:
        data = request.form
        
    db = SessionLocal()
    try:
        user = db.query(User).filter_by(username=data.get('username')).first() or \
               db.query(User).filter_by(email=data.get('username')).first()
    finally:
        db.close()
    
    try:
        if not user or not check_password_hash(user.hashed_password, data['password']):
            message = 'Credenciales inválidas'
            if request.is_json:
                return {'error': message}, 401
            flash(message, 'danger')
            return redirect(url_for('index'))
        
        access_token = create_access_token(identity=user.id)
        
        if request.is_json:
            return {
                'access_token': access_token,
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'username': user.username,
                    'role': user.role.name
                }
            }, 200
            
        response = make_response(redirect(url_for('admin.dashboard')))
        set_access_cookies(response, access_token)
        flash(f'Bienvenido, {user.username}!', 'success')
        return response
    finally:
        db.close()
    






@bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user() -> tuple[Dict[str, Any], int]:
    """Get current user information
    
    Returns:
        tuple[Dict[str, Any], int]: Response with user data and status code
    """
    user_id = get_jwt_identity()
    db = SessionLocal()
    try:
        user = db.query(User).get(user_id)
    finally:
        db.close()
    
    if not user:
        return {'error': 'User not found'}, 404
        
    return {
        'id': user.id,
        'email': user.email,
        'username': user.username,
        'role': user.role.name
    }, 200



@bp.route('/register', methods=['GET', 'POST'])
def register() -> Union[str, tuple[Dict[str, Any], int]]:
    """Register a new user
    
    Returns:
        Union[str, tuple[Dict[str, Any], int]]: Rendered template or API response
    """
    if request.method == 'GET':
        return render_template('auth/register.html')
        
    if request.is_json:
        data = request.get_json()
    else:
        data = request.form
    
    db = SessionLocal()
    try:
        if db.query(User).filter_by(email=data['email']).first():
            message = 'El correo electrónico ya está registrado'
            if request.is_json:
                return {'error': message}, 400
            flash(message, 'danger')
            return redirect(url_for('auth.register'))
            
        if db.query(User).filter_by(username=data['username']).first():
            message = 'El nombre de usuario ya está en uso'
            if request.is_json:
                return {'error': message}, 400
            flash(message, 'danger')
            return redirect(url_for('auth.register'))
        
        user = User(
            email=data['email'],
            username=data['username'],
            hashed_password=generate_password_hash(data['password']),
            full_name=data.get('full_name'),
            role=UserRole[data['role']]
        )
        
        db.add(user)
        db.commit()
        db.refresh(user)
    finally:
        db.close()
    
    message = 'Usuario registrado exitosamente'
    if request.is_json:
        return {'message': message}, 201
        
    flash(message, 'success')
    return redirect(url_for('auth.login'))


@bp.route('/forgot-password', methods=['GET'])
def forgot_password() -> str:
    """Show forgot password form
    
    Returns:
        str: Rendered template
    """
    return render_template('auth/forgot_password.html')

@bp.route('/logout')
@login_required
def logout() -> str:
    """Logout user
    
    Returns:
        str: Redirect response
    """
    response = make_response(redirect(url_for('auth.login')))
    unset_jwt_cookies(response)
    flash('Has cerrado sesión exitosamente.', 'success')
    return response
