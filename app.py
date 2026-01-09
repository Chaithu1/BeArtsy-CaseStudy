from flask import Flask

from config import init_datastore_client
from contracts import require_accept_json, reject_body
from users.routes import create_users_blueprint
from arts.routes import create_arts_blueprint
from galleries.routes import create_galleries_blueprint

def create_app() -> Flask:
    app = Flask(__name__)
    ds = init_datastore_client()

    @app.get("/")
    @require_accept_json
    @reject_body
    def health_check():
        return {"status": "ok"}, 200

    app.register_blueprint(create_users_blueprint(ds))
    app.register_blueprint(create_arts_blueprint(ds))
    app.register_blueprint(create_galleries_blueprint(ds))
    
    return app

if __name__ == "__main__":
    create_app().run(port=8080, debug=True)