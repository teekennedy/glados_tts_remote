#!/usr/bin/env python3

import os
import sys
import traceback
from urllib.parse import unquote

from flask import Flask, abort, make_response, request

from glados import tts_runner

app = Flask(__name__)


@app.route("/say")
def say():
    format = request.args.get("format", "wav")
    if format not in ["wav", "mp3"]:
        abort(400, "Unknown audio format")

    text = request.args.get("text", "")
    if len(text) == 0:
        # No text, no response
        return('', 204)

    # Generate New Sample
    try:
        audio_binary = glados.run_tts(unquote(text), format=format)
        response = make_response(audio_binary)
        response.headers.set("Content-Type", f"audio/{format}")
        return response
    except Exception as e:
        print(f"ERROR: Exception encountered while running tts: {e}")
        print(traceback.format_exc())
        abort(500)

@app.route("/health")
def health():
    return "OK"


current_dir = os.getcwd()
sys.path.insert(0, current_dir + "/glados_tts")

print("\033[1;94mINFO:\033[;97m Initializing TTS Engine...")

glados = tts_runner(False, True)


def glados_tts(text, alpha=1.0):

    glados.run_tts(text, alpha)
    return True


# If the script is run directly, assume remote engine
if __name__ == "__main__":

    # Remote Engine Veritables
    PORT = 8124
    DEBUG = True

    print("\033[1;94mINFO:\033[;97m Initializing TTS Server...")

    cli = sys.modules["flask.cli"]
    app.run(host="0.0.0.0", port=PORT)
