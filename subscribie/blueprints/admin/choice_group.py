from . import admin
from subscribie.auth import login_required
from subscribie.forms import ChoiceGroupForm, QuestionForm
from subscribie.models import ChoiceGroup, Plan, Question, PlanQuestionAssociation
from flask import request, render_template, url_for, flash, redirect
from subscribie.database import database


@admin.route("/add-choice-group", methods=["GET", "POST"])
@login_required
def add_choice_group():
    form = ChoiceGroupForm()
    if form.validate_on_submit():
        choice_group = ChoiceGroup()
        choice_group.title = request.form["title"]
        database.session.add(choice_group)
        database.session.commit()
        flash("Added new choice group")
        return redirect(url_for("admin.list_choice_groups"))

    return render_template("admin/choice_group/add_choice_group.html", form=form)


@admin.route("/list-choice-groups", methods=["GET", "POST"])
@login_required
def list_choice_groups():
    choice_groups = ChoiceGroup.query.all()
    questions = Question.query.all()
    return render_template(
        "admin/choice_group/list_choice_groups.html",
        choice_groups=choice_groups,
        questions=questions,
    )


@admin.route("/edit-choice-group/<id>", methods=["GET", "POST"])
@login_required
def edit_choice_group(id):
    choice_group = ChoiceGroup.query.get(id)
    if request.method == "POST":
        choice_group.title = request.form["title"]
        database.session.commit()
        flash("Choice group updated")
    return render_template(
        "admin/choice_group/edit_choice_group.html", choice_group=choice_group
    )


@admin.route("/choice-group/<choice_group_id>/assign-plan", methods=["GET", "POST"])
@login_required
def choice_group_assign_plan(choice_group_id):
    choice_group = ChoiceGroup.query.get(choice_group_id)
    plans = Plan.query.filter_by(archived=0)

    if request.method == "POST":
        # Remove choice group if not selected
        for plan in plans:
            if choice_group in plan.choice_groups:
                plan.choice_groups.remove(choice_group)

        for plan_id in request.form.getlist("assign"):
            plan = Plan.query.get(plan_id)
            plan.choice_groups.append(choice_group)

        database.session.commit()
        flash("Choice group has been added to selected plan(s)")
        return redirect(url_for("admin.list_choice_groups"))

    return render_template(
        "admin/choice_group/choice_group_assign_plan.html",
        choice_group=choice_group,
        plans=plans,
    )


@admin.route("/delete-choice-group/<id>", methods=["GET"])
@login_required
def delete_choice_group(id):
    if "confirm" in request.args:
        choice_groups = ChoiceGroup.query.all()

        return render_template(
            "admin/choice_group/list_choice_groups.html",
            choice_groups=choice_groups,
            choice_group=ChoiceGroup.query.get(id),
            confirm=False,
        )
    choice_group = ChoiceGroup.query.get(id)
    database.session.delete(choice_group)
    database.session.commit()
    flash("Choice group deleted")
    return redirect(url_for("admin.list_choice_groups"))


@admin.route("/list-questions", methods=["GET", "POST"])
@login_required
def list_questions():
    questions = Question.query.all()
    plans = Plan.query.all()

    return render_template(
        "admin/question/list_questions.html", questions=questions, plans=plans
    )


@admin.route("/add-question", methods=["GET", "POST"])
@login_required
def add_question():
    form = QuestionForm()
    if form.validate_on_submit():
        question = Question()
        question.title = request.form["title"]
        database.session.add(question)
        database.session.commit()
        flash("Added new question")
        return redirect(url_for("admin.list_questions"))

    return render_template("admin/choice_group/add_question.html", form=form)


@admin.route("/edit-question/<id>", methods=["GET", "POST"])
@login_required
def edit_question(id):
    question = Question.query.get(id)
    if request.method == "POST":
        question.title = request.form["title"]
        database.session.commit()
        flash("Question updated")
    return render_template("admin/question/edit_question.html", question=question)


@admin.route("/question/<question_id>/assign-plan", methods=["GET", "POST"])
@login_required
def question_assign_plan(question_id):
    question = Question.query.get(question_id)
    plans = Plan.query.filter_by(archived=0)

    if request.method == "POST":
        # Remove question associations
        for plan in plans:
            database.session.query(PlanQuestionAssociation).filter(
                PlanQuestionAssociation.plan_id == plan.id,
                PlanQuestionAssociation.question_id == question.id,
            ).delete()

        # Add back only selected question/plan associations
        for plan_id in request.form.getlist("assign"):
            plan = Plan.query.get(plan_id)
            plan_question_assoc = PlanQuestionAssociation()
            plan_question_assoc.question_id = question.id
            plan_question_assoc.plan_id = int(plan_id)
            database.session.add(plan_question_assoc)

        database.session.commit()
        flash("The question assignments have been applied to selected plan(s)")
        return redirect(url_for("admin.list_questions"))

    return render_template(
        "admin/question/question_assign_plan.html",
        question=question,
        plans=plans,
    )


@admin.route("/delete-question/<id>", methods=["GET"])
@login_required
def delete_question(id):
    if "confirm" in request.args:
        questions = Question.query.all()

        return render_template(
            "admin/question/list_questions.html",
            questions=questions,
            question=Question.query.get(id),
            is_question_delete_request=True,
            confirm=False,
        )
    question = Question.query.get(id)

    # Delete PlanQuestionAssociation with that question:
    database.session.query(PlanQuestionAssociation).filter(
        PlanQuestionAssociation.question_id == id
    ).delete()

    # Delete the question itself:
    database.session.delete(question)
    database.session.commit()

    flash("Question deleted")
    return redirect(url_for("admin.list_questions"))


@admin.route("/plan/questions/set-question-order/<plan_id>", methods=["GET", "POST"])
@login_required
def set_question_order_by_plan(plan_id):
    plan = Plan.query.get(plan_id)

    if request.method == "POST":
        """
        For each question passed, get & and save the chosen order for
        the appearance order
        """
        for plan_question_assoc_id in request.form.getlist("plan_question_assoc_id"):
            order_value = int(
                request.form.get(
                    f"order-value-for-question_assoc-id-{plan_question_assoc_id}"
                )
            )
            question_id = int(
                request.form.get(
                    f"question_id-for-question_assoc-id-{plan_question_assoc_id}"
                )
            )
            # Get by composite key (question_id, plan_id)
            plan_question_association = PlanQuestionAssociation.query.get(
                (question_id, plan.id)
            )
            plan_question_association.order = order_value
            database.session.add(plan_question_association)

        database.session.commit()
        flash("The plans question's have been ordered")
        return redirect(url_for("admin.set_question_order_by_plan", plan_id=plan.id))

    # Sort questions by order
    plan.questions.sort(key=lambda question: question.order or 0)

    return render_template(
        "admin/question/set_question_order.html",
        plan=plan,
    )
