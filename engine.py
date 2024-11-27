#!/usr/bin/env python3

import os
import sys

from flask import Flask, abort, make_response, request

from glados import tts_runner

app = Flask(__name__)


@app.route("/say")
def say():
    text = request.args.get("text", None)
    if text is None:
        abort(400)

    # Generate New Sample
    try:
        wav_binary = glados.run_tts(text)
        response = make_response(wav_binary)
        response.headers.set("Content-Type", "audio/wav")
        return response
    except Exception as e:
        print(f"ERROR: Exception encountered while running tts: {e}")
        abort(500)


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
