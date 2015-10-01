from flask import Blueprint, abort, redirect, render_template, current_app
import json
import functools
import database_helper

redir_page = Blueprint("redirect", __name__)


# Routes


@redir_page.route("/")
def root():
    return redirect(current_app.config["DEFAULT_URL"], 301)


@redir_page.route("/<shortcode>")
def target(shortcode):
    is_view = False
    if shortcode[-1:] == "+":
        shortcode = shortcode[:-1]
        is_view = True

    result = database_helper.get_shortcode_target(shortcode)
    if result == None:
        return abort(404)

    if is_view:
        return render_template("index_view.html", shortcode=shortcode, data=result, sitename=current_app.config["SITENAME"])

    if result.is_random:
        code = 301
    else:
        code = 307
    
    return redirect(result.target_url, code)
