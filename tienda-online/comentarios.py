from flask import Blueprint, render_template

comentarios_bp = Blueprint('comentarios', __name__)

@comentarios_bp.route('/comentarios')
def mostrar_comentarios():
    return "<h2>Aquí irán los comentarios del producto</h2>"
