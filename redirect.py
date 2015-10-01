from flask import Blueprint, abort, redirect, current_app
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
    result = database_helper.get_shortcode_target(shortcode)
    if result == None:
        return abort(404)

    if result.is_random:
        code = 301
    else:
        code = 307
    
    return redirect(result.target_url, code)
