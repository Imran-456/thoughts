from src import app, db
from src.models import post, user

if __name__ == "__main__":
    app.run(debug=True)
    # with app.app_context():
    #     db.create_all()

