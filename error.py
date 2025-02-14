from flask import render_template

# Oma sivunsa mahdollisia virhetilanteita varten
def page(message, type):
    return render_template("error.html", message=message, type=type)