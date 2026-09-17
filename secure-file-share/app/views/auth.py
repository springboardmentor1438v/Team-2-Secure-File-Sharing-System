from __future__ import annotations

import sqlite3

from flask import (Blueprint, abort, flash, redirect, render_template, request,
                   session, url_for)

from ..db import get_db
from ..security import (EMAIL_RE, audit, current_user, hash_password,
                        password_problem, rate_limit, require_csrf,
                        utcnow_iso, verify_password)

bp = Blueprint("auth", __name__)


@bp.before_request
def csrf_guard():
    require_csrf()


@bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user():
        return redirect(url_for("files.dashboard"))

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        if not EMAIL_RE.match(email):
            flash("Enter a valid email address.", "error")
        elif (problem := password_problem(password)) is not None:
            flash(problem, "error")
        else:
            try:
                db = get_db()
                cur = db.execute(
                    "INSERT INTO users (email, password_hash, created_at) VALUES (?,?,?)",
                    (email, hash_password(password), utcnow_iso()),
                )
                db.commit()
            except sqlite3.IntegrityError:
                flash("That email is already registered.", "error")
            else:
                session.clear()
                session["uid"] = cur.lastrowid
                session.permanent = True
                audit("account.created", target=email)
                return redirect(url_for("files.dashboard"))

    return render_template("register.html")


@bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user():
        return redirect(url_for("files.dashboard"))

    if request.method == "POST":
        limit, window = 8, 300
        if not rate_limit("login", limit, window):
            abort(429, description="Too many sign-in attempts. Try again in a few minutes.")

        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        row = get_db().execute(
            "SELECT id, password_hash FROM users WHERE email = ? AND is_active = 1",
            (email,),
        ).fetchone()

        # Same message either way: do not reveal which emails exist.
        if row and verify_password(row["password_hash"], password):
            session.clear()
            session["uid"] = row["id"]
            session.permanent = True
            audit("session.started", target=email)
            nxt = request.form.get("next") or request.args.get("next") or ""
            if nxt.startswith("/") and not nxt.startswith("//"):
                return redirect(nxt)
            return redirect(url_for("files.dashboard"))
        flash("Email or password is incorrect.", "error")

    return render_template("login.html", next=request.args.get("next", ""))


@bp.post("/logout")
def logout():
    audit("session.ended")
    session.clear()
    return redirect(url_for("auth.login"))
