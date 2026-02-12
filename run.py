import os
from dotenv import load_dotenv

load_dotenv()

from app import create_app
from app.db import ensure_schema

app = create_app()
ensure_schema()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)