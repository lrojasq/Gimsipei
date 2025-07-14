from flask import Flask, render_template, redirect, url_for
from flask_mysqldb import MySQL, MySQLdb

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__, 
    template_folder='src/templates',
    static_folder='src/static'
)

# Configure app
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# JWT Configuration
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')
app.config['JWT_TOKEN_LOCATION'] = ['cookies']
app.config['JWT_COOKIE_SECURE'] = False  # Set to True in production
app.config['JWT_COOKIE_CSRF_PROTECT'] = True
app.config['JWT_ACCESS_COOKIE_PATH'] = '/'
app.config['JWT_REFRESH_COOKIE_PATH'] = '/auth/refresh'
app.config['JWT_COOKIE_SAMESITE'] = 'Lax'

# Initialize extensions
jwt = JWTManager(app)
CORS(app)

# Import models
from src.models.user import User
from src.models.document import Document
from src.models.exercise import Exercise
from src.models.assignment import Assignment
from src.models.submission import Submission

# Create database tables
Base.metadata.create_all(bind=engine)

def init_routes():
    # Import routes
    from src.routes import auth, documents, exercises, assignments, admin

    # Register blueprints
    app.register_blueprint(auth.bp)
    app.register_blueprint(documents.bp)
    app.register_blueprint(exercises.bp)
    app.register_blueprint(assignments.bp)
    app.register_blueprint(admin.bp)

# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

# Health check endpoint
@app.route('/health')
def health_check():
    return jsonify({'status': 'healthy'}), 200



# Rutas
@app.route('/', methods=['GET','POST'])
def index():
    return redirect(url_for('login'))


@app.route('/login', methods=['GET','POST'])
def login():
     return render_template('auth/login.html')
 
 
@app.route('/user', methods=['GET','POST'])
def user():
    return render_template('auth/user.html')




if __name__ == '__main__':
    port = int(os.getenv('PORT', 5010))
    app.run(host='0.0.0.0', port=port, debug=os.getenv('FLASK_ENV') == 'development')