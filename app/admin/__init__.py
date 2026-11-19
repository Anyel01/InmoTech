"""
Panel de administración (rol ADMINISTRADOR).

Tiene su propio blueprint y su propia pila: routes -> services -> repositories,
igual que el resto de la aplicación pero separada, porque es un subsistema
completo. Todas las rutas viven bajo /admin.
"""

from flask import Blueprint

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

from app.admin import routes  # noqa: E402,F401  (registra las rutas en admin_bp)
