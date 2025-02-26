"""Module for rendering error pages"""

from flask import render_template

# Render error page
def page(message, error_type):
    """
    Renders an error page with the given message and error type.
    Args:
        message: displayed error message.
        error_type: type of encountered error.
    Returns:
        rendered HTML error page.
    """
    return render_template("error.html", message=message, error_type=error_type)
