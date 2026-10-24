import asyncio
import pathlib
import subprocess
from threading import Thread
from typing import TextIO

import obspython as obs

from src.mpris import MPRIS

proc = None
script_location = "./src/main.py"


def stream_output(stream: TextIO, label: str = ""):
    try:
        for line in stream:
            print(f"{label}{line}", end="", flush=True)
    finally:
        stream.close()


def kill_process():
    if proc is None or proc.poll() is not None:
        print("No process found")
        return

    proc.terminate()
    print("Terminating process...")
    try:
        proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        print("Termination timed out, forcibly killing process...")
        proc.kill()
        proc.wait()

def start_process(settings):
    global proc
    print("Starting process...")

    player = obs.obs_data_get_string(settings, "player")
    print("Selected player:", player)
    port = obs.obs_data_get_int(settings, "port")
    print("Selected port:", port)
    try:
        proc = subprocess.Popen(["python", "-u",
                                script_location,
                                str(player),
                                str(port)],
                cwd=pathlib.Path(__file__).parent.resolve(),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                start_new_session=True
        )
        Thread(target=stream_output, args=(proc.stdout,), daemon=True).start()
        Thread(
            target=stream_output,
            args=(proc.stderr, "[overlay stderr] "),
            daemon=True,
        ).start()
    except Exception as e:
        print(e)

def script_properties():
    props = obs.obs_properties_create()

    obs.obs_properties_add_int(props, "port", "Port", 1024, 65535, 1)
    p_list = obs.obs_properties_add_list(props, "player", "Player", obs.OBS_COMBO_TYPE_EDITABLE, obs.OBS_COMBO_FORMAT_STRING)
    players = asyncio.run(MPRIS.get_players())
    for player in players:
        obs.obs_property_list_add_string(p_list, player, player)

    return props

def script_defaults(settings):
    obs.obs_data_set_default_int(settings, "port", 5000)

def script_description():
    return "Overlay to show what you're currently listening to using HTML5 and MPRIS\n\nCreated by leician"

def script_load(settings):
    start_process(settings)

def script_update(settings):
    kill_process()
    start_process(settings)
    
def script_unload():
    kill_process()