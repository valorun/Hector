import logging
from .model import Intent
import json
from cipher import mqtt
from cipher.core.sequence_reader import sequence_reader
from cipher.core.actions import ScriptAction

@mqtt.on_topic('hermes/intent/#')
def handle_intents(client, userdata, message):
    intent = message.payload.decode('utf-8')
    try:
        intent = json.loads(intent)
    except Exception:
        return
    intent_name = intent['intent']['intentName']
    logging.info("Received intent '" + intent_name + "' with slots '" + str(intent['slots']) + "'")
    db_intent = Intent.query.filter_by(intent=intent_name).first()
    kwargs = {}
    kwargs['slots'] = intent['slots']
    if(db_intent is not None):
        if db_intent.sequence is not None:
            sequence_reader.launch_sequence(db_intent.sequence.id, **kwargs)
        elif db_intent.script_name is not None:
            ScriptAction(db_intent.script_name).execute(**kwargs)
