from flask import Flask, render_template
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'mi_servidor_flask_secret_2026')
app.config['MAX_CONTENT_LENGTH'] = 3 * 1024 * 1024  # 3MB

# Register blueprints
from routes.auth_routes import auth_bp
from routes.crud_routes import crud_bp
from routes.ftp_routes import ftp_bp
from routes.seguridad_routes import seguridad_bp
from routes.static_routes import static_bp

app.register_blueprint(auth_bp)
app.register_blueprint(crud_bp)
app.register_blueprint(ftp_bp)
app.register_blueprint(seguridad_bp)
app.register_blueprint(static_bp)

# Serve uploads
from flask import send_from_directory

@app.route('/uploads/<path:filename>')
def uploads(filename):
    return send_from_directory('uploads', filename)

# Error handlers
@app.errorhandler(404)
def not_found(e):
    return render_template('error.html', code=404, message='La página solicitada no existe.'), 404

@app.errorhandler(500)
def server_error(e):
    return render_template('error.html', code=500, message=str(e) or 'Ocurrió un error inesperado.'), 500

if __name__ == '__main__':
    port = int(os.getenv('PORT', 3000))
    app.run(host='0.0.0.0', port=port)
