from flask import Flask, g
import admin, redirect
from database import init_db, db_session


init_db()

app = Flask(__name__)

app.config.from_pyfile('data/hybridius.settings')

app.register_blueprint(admin.admin_page, url_prefix="/admin")
app.register_blueprint(redirect.redir_page)


@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()


if __name__ == "__main__":
    app.config["dev_mode"] = True
    app.run(host="127.0.0.1", debug=True)
