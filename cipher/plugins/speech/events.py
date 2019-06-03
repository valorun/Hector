import logging
from cipher.model import db, Intent
import json
from cipher import mqtt
from cipher.core.sequence_reader import sequence_reader
from cipher.core.actions import speech

mqtt.subscribe('hermes/intent/#')

@mqtt.on_topic('hermes/intent/#')
def handle_intents(client, userdata, message):
	intent = message.payload.decode('utf-8').rsplit('/',1)[1]
	logging.info(intent)
	db_intent = Intent.query.filter_by(intent=intent).first()
	slots = {}
	if(db_intent != None):
		speech(db_intent.response)
		sequence_reader.launchSequence(db_intent.sequence, **slots)

