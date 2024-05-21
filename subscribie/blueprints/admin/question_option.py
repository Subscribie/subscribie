from . import admin
from subscribie.auth import login_required
from subscribie.forms import QuestionOptionForm
from subscribie.models import Question, QuestionOption
from subscribie.database import database
from flask import request, render_template, url_for, flash, redirect


@admin.route("/add-question-option/question_id/<question_id>", methods=["GET", "POST"])
@login_required
def add_question_option(question_id):
    form = QuestionOptionForm()
    question = Question.query.get(question_id)
    if form.validate_on_submit():
        question_option = QuestionOption()
        question_option.title = request.form["title"]
        question.options.append(question_option)
        database.session.commit()
        flash("Added new question option")
        return redirect(url_for("admin.list_question_options", question_id=question_id))

    return render_template("admin/question_option/add_question_option.html", form=form)


@admin.route("/list-question-options/<question_id>", methods=["GET", "POST"])
@login_required
def list_question_options(question_id):
    question = Question.query.get(question_id)
    return render_template(
        "admin/question_option/list_question_options.html", question=question
    )


@admin.route("/edit-question-option/<id>", methods=["GET", "POST"])
@login_required
def edit_question_option(id):
    question_option = QuestionOption.query.get(id)
    if request.method == "POST":
        question_option.title = request.form["title"]
        database.session.commit()
        flash("Question option updated")
    return render_template(
        "admin/question_option/edit_question_option.html",
        question_option=question_option,
    )


@admin.route(
    "/delete-question-option/<question_option_id>/question_id/<question_id>",
    methods=["GET"],
)
@login_required
def delete_question_option(question_option_id, question_id):
    question = Question.query.get(question_id)
    if "confirm" in request.args:
        question_options = QuestionOption.query.all()

        return render_template(
            "admin/question_option/list_question_options.html",
            question_options=question_options,
            question_option=QuestionOption.query.get(question_option_id),
            question=question,
            confirm=False,
        )
    question_option = QuestionOption.query.get(question_option_id)
    database.session.delete(question_option)
    database.session.commit()
    flash("Question option deleted")
    return redirect(url_for("admin.list_question_options", question_id=question.id))
