import asyncio
import sys
from threading import Thread

from flask import Flask

from mpris import MPRIS
from overlay import bp

player = sys.argv[1].strip() if len(sys.argv) > 1 else ""
port_arg = sys.argv[2].strip() if len(sys.argv) > 2 else ""

mpris = MPRIS(player) if player else None
port = int(port_arg) if port_arg else 5000

app = Flask(__name__, static_folder="../assets/static", template_folder="../assets/templates")
app.extensions["mpris"] = mpris
app.register_blueprint(bp)

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
def run_listener():
    if mpris is not None:
        try:
            asyncio.run(mpris.consume_metadata())
        except Exception:
            app.logger.exception("MPRIS listener stopped")
    else:
        return


def main():
    Thread(target=run_listener, daemon=True).start()
    app.run(host="127.0.0.1", port=port, debug=False)

main()
