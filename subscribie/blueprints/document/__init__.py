import logging
from flask import Blueprint, render_template, current_app
from subscribie.models import Document
import jinja2

log = logging.getLogger(__name__)
document_blueprint = Blueprint("document", __name__, template_folder="templates")


@document_blueprint.route("/document/<document_uuid>", methods=["GET"])
def show_document(document_uuid):
    """Show raw document"""
    document = Document.query.where(Document.uuid == document_uuid).first()
    if document is not None:
        if document.body is None:
            return f"The document '{document.name}' is empty"
        environment = jinja2.Environment(
            loader=jinja2.FileSystemLoader(str(current_app.config["THEME_PATH"]))
        ).from_string(document.body)

        return environment.render()
    else:
        return "Document not found", 404


@document_blueprint.route("/documents", methods=["GET"])
def list_documents():
    """List all documents"""
    documents = Document.query.all()

    if len(documents) != 0:
        return render_template("list_documents.html", documents=documents)
    else:
        return "There are no documents", 404
