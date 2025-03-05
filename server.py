from app import app, db

# Ensure tables are created before running the server
with app.app_context():
    db.create_all()

if __name__ == "__main__":
    from gunicorn.app.wsgiapp import run
    run()