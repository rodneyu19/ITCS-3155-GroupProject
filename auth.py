from flask import Blueprint, redirect, url_for, session
from flask_dance.contrib.spotify import make_spotify_blueprint, spotify

auth_bp = Blueprint("auth", __name__)

spotify_bp = make_spotify_blueprint(
    client_id="YOUR_SPOTIFY_CLIENT_ID",
    client_secret="YOUR_SPOTIFY_CLIENT_SECRET",
    scope="user-library-read user-read-email",
    redirect_to="index"
)
auth_bp.register_blueprint(spotify_bp, url_prefix="/spotify_login")

@auth_bp.route("/login")
def login():
    if not spotify.authorized: # type: ignore
        return redirect(url_for("spotify.login"))
    return redirect(url_for("index"))

@auth_bp.route("/logout")
def logout():
    if 'spotify_oauth' in session:
        del session['spotify_oauth']
    return redirect(url_for("index"))
