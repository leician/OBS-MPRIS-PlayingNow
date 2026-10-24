from flask import Blueprint, current_app, jsonify, render_template

bp = Blueprint("overlay", __name__)

@bp.route("/")
def overlay():
    mpris = current_app.extensions["mpris"]
    if mpris is None:
        return render_template("no_player.html")
    else:
        return render_template("index.html")

@bp.route("/api/metadata", methods=["GET"])
async def get_metadata():
    mpris = current_app.extensions["mpris"]
    if mpris is None:
        return "fuckoff"

    with mpris.metadata_lock:
        metadata = mpris.latest_metadata.copy()

    return jsonify({
        "title": metadata.get("title"),
        "artist": ", ".join(metadata.get("artists")),
        "cover": metadata.get("cover"),
        "status": metadata.get("status")
    })