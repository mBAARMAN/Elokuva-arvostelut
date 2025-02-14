from flask import render_template

def page(message, type):
    return render_template("error.html", message=message, type=type)