from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, RadioField
import datetime
from random import choice
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config['SECRET_KEY'] = "123456789"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///tasks.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = "False"
Bootstrap(app)

db = SQLAlchemy(app)

class Tasks(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    task_heading = db.Column(db.String)
    task_details = db.Column(db.String)
    task_date = db.Column(db.String)
    task_importance = db.Column(db.String)

class Notes(db.Model):
    __tablename__ = "Notes"
    id = db.Column(db.Integer, primary_key=True)
    note_details = db.Column(db.String)


class Forms(FlaskForm):
    subject = StringField('Subject')
    content = StringField('Task details/Importance Level')
    importance_level = RadioField(label="importance", choices=["Low", "Medium", "High"])
    submit = SubmitField(label="Submit")



@app.route("/", methods=['GET', "POST"])
def home():
    all_tasks = Tasks.query.all()
    if request.args.get("task"):
        task = Tasks.query.filter_by(id=int(request.args.get("task")) + 1).all()
        db.session.delete(task)
        db.session.commit()

        return redirect(url_for('home'))



    if request.args.get("level"):
        if request.args.get("level") == "low":
            all_tasks = Tasks.query.filter_by(task_importance='Low').all()
            print(all_tasks)
            return render_template("index.html", all_tasks=all_tasks)
        elif request.args.get("level") == "medium":
            all_tasks = Tasks.query.filter_by(task_importance='Medium').all()
            return render_template("index.html", all_tasks=all_tasks)
        elif request.args.get("level") == "high":
            all_tasks = Tasks.query.filter_by(task_importance='High').all()
            return render_template("index.html", all_tasks=all_tasks)


    return render_template("index.html", all_tasks=all_tasks)


@app.route("/notes", methods=["POST", "GET"])
def notes_tab():
    notes = Notes.query.all()
    colors = ["#FCFFA6", "#C1FFD7", "#B5DEFF", "#CAB8FF", "#D77FA1"]
    random_color = choice(colors)
    if request.form.get('submit'):
        note = request.form["text"]
        add_note = Notes(
            note_details=note
        )
        db.session.add(add_note)
        db.session.commit()
        return redirect(url_for("notes_tab"))
    return render_template("notes.html", notes=notes, color=random_color)

@app.route("/remove")
def remove():
    task_id = request.args.get("id")
    task_to_remove = Tasks.query.get(task_id)
    db.session.delete(task_to_remove)
    db.session.commit()
    return redirect(url_for('.home'))

@app.route("/add_task", methods=["GET", "POST"])
def add_task():
    form = Forms()
    if form.validate_on_submit():
        task = Tasks(task_heading=request.form.get('subject'), task_details=request.form.get('content'), task_date=datetime.datetime.now().strftime("%b, %d"), task_importance=request.form.get('importance_level'))

        db.session.add(task)
        db.session.commit()
        return redirect(url_for('home', form=task))
    return render_template("add_task.html", form=form)


if __name__ == "__main__":
    app.run(debug=True)