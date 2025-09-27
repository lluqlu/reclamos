from flask import Flask
from config import DATA_DIR
from web.reclamos_bp import bp as reclamos_bp




def create_app():
    app = Flask(__name__)
    # Blueprints
    app.register_blueprint(reclamos_bp)
    # Asegura carpeta de datos
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    return app




if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, port=5001)
