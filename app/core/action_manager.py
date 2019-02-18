import logging
import json
import importlib.util
import os
from os.path import join
from flask_socketio import SocketIO, emit
from flask_mqtt import Mqtt
from app import socketio, mqtt
from app.constants import SCRIPTS_LOCATION, SOUNDS_LOCATION
from app.model import db, Relay, config

def speech(speech):
	"""
	Speak on the client from the client or from the raspberry, according to the parameter
	"""
	if(speech == None):
		return
	socketio.emit("response", speech, namespace="/client")

def relay(rel_label, rel_state=None):
	"""
	Activate the relay with the specified label
	"""
	if rel_state != 1 and rel_state != 0:
		rel_state=""
	with db.app.app_context():
		db_rel = Relay.query.filter_by(label=rel_label).first()
		if(not db_rel.enabled):
				return
		pin = db_rel.pin
		parity = db_rel.parity
		raspi_id = db_rel.raspi_id

		#if the relay is paired
		if(parity!=""):
			#recover all the peer relays
			peers_rel = Relay.query.filter(Relay.parity==parity, Relay.label!=rel_label)
			peers=[]
			for peer in peers_rel:
				peers.append(peer.pin)
			#activate the relay on the corresponding raspberry
			mqtt.publish('raspi/'+raspi_id+'/relay/activate', json.dumps({'gpio':pin, 'state':rel_state, 'peers':peers}))
			#socketio.emit("activate_paired_relay", (pin, rel_state, peers, raspi_id), namespace="/relay", broadcast=True)

		else:
			mqtt.publish('raspi/'+raspi_id+'/relay/activate', json.dumps({'gpio':pin, 'state':rel_state, 'peers':None}))
			#socketio.emit("activate_relay", (pin, rel_state, raspi_id), namespace="/relay")

def motion(m1, m2):
	"""
	Activate the motors with the specified speed
	"""
	if config.getMotionRaspiId() == None:
		return
	mqtt.publish('raspi/'+config.getMotionRaspiId()+'/motion', json.dumps({'m1':m1, 'm2':m2}))
	
def servo(index):
	"""
	Launch a servomotor sequence with the given id
	"""
	if config.getServoRaspiId() == None:
		return
	mqtt.publish('raspi/'+config.getServoRaspiId()+'/servo', json.dumps({'index':index}))

def sound(sound_name):
	"""
	Execute the requested sound from the 'sounds' directory
	"""
	if config.getAudioOnServer():
		os.system("sudo pkill mplayer")
		os.system("mplayer "+join(SOUNDS_LOCATION, sound_name).replace(" ", "\\ "))
		logging.info("Playing sound \'" + join(SOUNDS_LOCATION, sound_name) + "\' on server")			
	else:
		socketio.emit("play_sound", sound_name, namespace="/client")

def script(script_name, **kwargs):
	"""
	Import the requested script from the 'scripts' directory and execute its 'main' method
	"""
	spec = importlib.util.spec_from_file_location("script", os.path.join(SCRIPTS_LOCATION, script_name))
	script = importlib.util.module_from_spec(spec)
	spec.loader.exec_module(script)
	socketio.emit("response", script.main(**kwargs), namespace="/client")