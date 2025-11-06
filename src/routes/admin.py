from flask import Blueprint, render_template
from src.routes.auth import login_required

bp = Blueprint('admin', __name__, url_prefix='/admin', template_folder='templates')

@bp.route('/dashboard')
@login_required
def dashboard():
    return render_template('admin/dashboard.html')
