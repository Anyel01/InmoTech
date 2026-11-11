

import os

from dotenv import load_dotenv

# El .env debe cargarse antes de crear la app para que la configuración lo vea
load_dotenv()

from app import create_app  # noqa: E402

app = create_app()

if __name__ == '__main__':
    host = os.environ.get('HOST', '127.0.0.1')
    puerto = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', '1') == '1'
    print(f"InmoTech corriendo en http://{host}:{puerto}")
    app.run(host=host, port=puerto, debug=debug)
