from functools import wraps
import random, string, json
from flask import abort, Blueprint, request, redirect, Response, render_template, flash, url_for, current_app, session

from forms import AddForm, LoginForm
import database_helper


admin_page = Blueprint("admin", __name__)


# General helpers


def get_random_shortcode(length):
    return ''.join(random.SystemRandom().choice(string.ascii_lowercase + string.digits) for _ in range(length))


def url_for_code(shortcode, target_url):
    return "<a href=\"%s\">%s</a>" % (url_for("redirect.target", shortcode=shortcode), target_url)


# Blueprint stuff


def check_auth(username, password):
    return username == current_app.config["ADMIN_USER"] and password == current_app.config["ADMIN_PASS"]


def check_session_auth():
    return "authorization" in session and session["authorization"] == "Yes"


def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not check_session_auth():
            return redirect(url_for(".login"))
        return f(*args, **kwargs)
    return decorated


@admin_page.before_request
def require_https():
    if not "dev_mode" in current_app.config and request.headers.get("X-Forwarded-Proto", "http") != "https":
        return redirect(request.url.replace("http://", "https://"))


# Routes


@admin_page.route("/")
@requires_auth
def index():
    return render_template("admin_index.html")


@admin_page.route("/login", methods=["GET", "POST"])
def login():
    if check_session_auth():
        return redirect(url_for(".index"))

    form = LoginForm(request.form)
    form.login_validator = check_auth
    if request.method != "POST" or not form.validate():
        return render_template("admin_login.html", login_form=form)

    # Login successful
    session["authorization"] = "Yes"

    return redirect(url_for(".index"))


@admin_page.route("/list")
@requires_auth
def list():
    results = database_helper.get_all()
    random = []
    nonrandom = []

    for r in results:
        if r.is_random:
            pool = random
        else:
            pool = nonrandom
        pool.append({
            "shortcode": r.shortcode,
            "target_url": r.target_url
        })

    dump = {"random": random, "nonrandom": nonrandom}

    return render_template("admin_list.html", results=dump)


@admin_page.route("/export")
@requires_auth
def export():
    results = database_helper.get_all()
    arr = map(lambda a: { "is_random": a.is_random, "shortcode": a.shortcode, "target_url": a.target_url }, results)
    js = json.dumps(arr)
    return Response(js, 200, {"Content-Type": "application/json"})


@admin_page.route("/add", methods=["GET", "POST"])
@requires_auth
def add():
    form = AddForm(request.form)
    if request.method != "POST" or not form.validate():
        return render_template("admin_add.html", add_form=form)

    shortcode = form.shortcode.data
    target_url = form.target_url.data
    random = form.is_random.data

    if (not shortcode or len(shortcode) == 0) and not random:
        return abort("No shortcode specified.", 400)

    if random:
        # Make sure the target doesn't already have a random shortcode
        target = database_helper.find_by_target(target_url)
        if target and target.is_random:
            flash("Shortcode '%s' for this URL already exists. %s" % (target.shortcode, url_for_code(target.shortcode, target.target_url)), category="info")
            return render_template("admin_add.html", add_form=form)

        # Find an unused random shortcode
        count = 0
        while True:
            shortcode = get_random_shortcode(current_app.config["SHORTCODE_LENGTH"])
            if database_helper.get_shortcode_target(shortcode) is None:
                break
                
            # Make sure we don't loop endlessly
            count = count + 1
            if count > 4:
                flash("Could not find usable shortcode after 5 tries.", category="danger")
                return render_template("admin_add.html", add_form=form)
    else:
        # Make sure this shortcode doesn't already exist
        target = database_helper.get_shortcode_target(shortcode)
        if target:
            flash("Shortcode '%s' already exists to %s." % (shortcode, target.target_url), category="warning")
            return render_template("admin_add.html", add_form=form)

    if database_helper.insert_shortcode(shortcode, target_url, random):
        msg = "Shortcode '%s' added successfully. %s" % (shortcode, url_for_code(shortcode, target_url))
        category = "success"
    else:
        msg = "Failed to create shortcode."
        category = "danger"

    flash(msg, category)
    return redirect(url_for(".add"))


@admin_page.route("/edit/<shortcode>", methods=["GET", "POST"])
@requires_auth
def edit(shortcode):
    result = database_helper.get_shortcode_target(shortcode)
    if result is None:
        return abort(404)

    form = AddForm(request.form, obj=result)
    if request.method != "POST" or not form.validate():
        return render_template("admin_edit.html", add_form=form, data=result)

    target_url = form.target_url.data

    if database_helper.update_shortcode(shortcode, target_url):
        msg = "Shortcode '%s' updated successfully. %s" % (shortcode, url_for_code(shortcode, target_url))
        category = "success"
    else:
        msg = "Failed to update shortcode."
        category = "danger"

    flash(msg, category)
    return redirect(url_for(".list"))


@admin_page.route("/delete/<shortcode>", methods=["GET", "POST"])
@requires_auth
def delete(shortcode):
    result = database_helper.get_shortcode_target(shortcode)
    if result is None:
        return abort(404)

    if request.method != "POST":
        return render_template("admin_delete.html", data=result)

    if database_helper.delete_shortcode(shortcode):
        msg = "Shortcode '%s' was deleted." % (shortcode)
        category = "success"
    else:
        msg = "Failed to remove shortcode."
        category = "warn"

    flash(msg, category=category)
    return redirect(url_for(".list"))
