from app import create_app
from app.db import ensure_schema

app = create_app()
ensure_schema()

if __name__=="__main__":
    app.run(debug=True)