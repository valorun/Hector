import logging
from flask import Flask, request, jsonify
import json
from . import commands
from cipher.model import Sequence, Relay, config, resources
from cipher.security import login_required

@commands.route('/commands')
@login_required
def commands_page():
    sequences=Sequence.query.all()
    relays=Relay.query.all()
    cameraUrl=config.getCameraUrl()
    sounds=resources.getSounds()
    motionRaspiId=config.getMotionRaspiId() # used to check if a raspi is specified, if not, then hide the motion panel
    return commands.render_page('commands.html', sequences=sequences, relays=relays, sounds=sounds, cameraUrl=cameraUrl, motionRaspiId=motionRaspiId)


@commands.route('/save_buttons', methods=['POST'])
@login_required
def save_buttons():
    """
    Save the grid of buttons on the server.
    """
    logging.info("Saving buttons grid")
    data=request.form.get("data")
    try:
        data = json.loads(data)
    except (ValueError, Exception):
        data = None
    config.setCommandsGrid(data)
    return "Grille sauvegardée.", 200

@commands.route('/load_buttons', methods=['POST'])
@login_required
def load_buttons():
    """  
    Load the grid of buttons from the server.
    """
    logging.info("Loading buttons grid")
    grid = config.getCommandsGrid()
    return jsonify(grid)