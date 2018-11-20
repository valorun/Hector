#!/usr/bin/python
# coding: utf-8

import logging
import time
import json
import importlib.util
import os
from os.path import join
from flask import current_app
from flask_socketio import SocketIO, emit
from .. import socketio
from app.constants import SCRIPTS_LOCATION, SOUNDS_LOCATION
import asyncio
from app.model import db, Relay, Sequence, chatbot, config
from app.chatbot.entity_adapter import ENTITY_PATTERN

class SequenceReader:
	"""
	Classe permettant de lire une sequence ou d'executer une action.
	"""
	def __init__(self):
		#nombre d'actions en cours, qu'il faut donc attendre avant d'executer une autre séquence
		self.threads = 0

	def executeSequence(self, app, startNode, nodes, edges, args=None):
		"""
		Lance l'execution de la séquence,place chaque nouvelle branche dans un thread différent.
		"""
		self.threads+=1
		self.executeAction(app, self.getNodeLabel(startNode, nodes), args)
		for c in self.getChildren(startNode, edges):
			socketio.start_background_task(self.executeSequence, app, c, nodes, edges, args)
		self.threads-=1

	def executeAction(self, app, label, args=None):
		"""
		Execute une action suivant un label donné, par exemple 'sleep:100ms'.
		"""
		if(len(label.split(":", 1))<2):
			return
		action=label.split(":", 1)[0]
		option=label.split(":", 1)[1]

		if(action=="pause"):
			#si c'est une pause, l'execution du script se met en pause
			socketio.sleep( int(option.split("ms")[0])/1000 )
		elif(action=="speech"):
			#si c'est une parole, on retourne le tout directement au client
			speech=option.split('"')[0]
			if args != None:
				speech=speech.replace(ENTITY_PATTERN, args[0])
			socketio.emit("response", speech, namespace="/client")
		elif(action=="relay"):
			#si c'est un relai, cherche d'abord le pin associé, reconstitue la requete
			rel_label = option.rsplit(',',1)[0]
			rel_state=""
			#si un état est spécifié (0 ou 1)
			if(len(option.rsplit(',',1))>1):
				rel_state=option.rsplit(',',1)[1]
			with app.app_context():
				db_rel = Relay.query.filter_by(label=rel_label).first()
				if(not db_rel.enabled):
					return
				pin = db_rel.pin
				parity = db_rel.parity
				raspi_id = db_rel.raspi_id

				#si le relai est appairé
				if(parity!=""):
					#on récupère tout les relais pairs
					peers_rel = Relay.query.filter(Relay.parity==parity, Relay.label!=rel_label)
					peers=[]
					for peer in peers_rel:
						peers.append(peer.pin)

					socketio.emit("activate_paired_relay", (pin, rel_state, peers, raspi_id), namespace="/relay", broadcast=True)

				else:
					socketio.emit("activate_relay", (pin, rel_state, raspi_id), namespace="/relay")
		elif(action=="script"):
			#si c'est un script, execute importe le script demandé et execute sa methode start
			spec = importlib.util.spec_from_file_location("script", os.path.join(SCRIPTS_LOCATION, option))
			script = importlib.util.module_from_spec(spec)
			spec.loader.exec_module(script)
			socketio.emit("response", script.start(args), namespace="/client")
		elif(action=="sound"):
			#si c'est un son, execute le son demandé
			if config.getAudioOnServer:
				os.system("pkill mplayer")
				os.system("mplayer "+join(SOUNDS_LOCATION,option))
			else:
				socketio.emit("play_sound", option, namespace="/client")
		else:
			#envoie de la commande aux raspberries
			logging.info("Sending "+action+" to rasperries.")
			socketio.emit("command", option, namespace="/"+action)
		logging.info(label)

	def getChildren(self, id, edges):
		"""
		Retourne la liste des id des noeuds enfants.
		"""
		children=[]
		for e in edges:
			if(e["from"]==id):
				children.append(e["to"])
		return children

	def getNodeLabel(self, id, nodes):
		"""
		Retourne le label du noeud avec l'id donné.
		"""
		for n in nodes:
			if(n["id"]==id):
				return n["label"]

	def readSequence(self, app, json, args=None):
		"""
		Lance l'execution d'une sequence cntenue dans un objet JSON.
		"""
		if(self.threads>0): #on attend que la séquence en cours soit achevée pour en lancer une nouvelle
			return
		nodes=json[0]
		edges=json[1]
		self.executeSequence(app, "start", nodes, edges, args)


sequence_reader = SequenceReader()


@socketio.on('speech_detected', namespace='/client')
def speech_detected(transcript):
	"""
	Fonction appelée lors de la détection d'une parole sur le client.
	"""
	logging.info("Received data: " + transcript)
	response = chatbot.getResponse(transcript)
	response_text = response.text

	if(len(response_text.split("]"))>1):
		seq_name=response_text.split("[")[1].split("]")[0]
		seq = Sequence.query.filter_by(id=seq_name).first()
		response_text = response_text.split("]")[1]
		#Si une séquence existe et est activée, on la lance
		if(seq!=None and seq.enabled):
			seq_data = seq.value
			logging.info('Executing sequence: '+seq_name)
			entities=None
			if hasattr(response, 'entities'): #Si des entités sont détectées, on les passera à la séquence
				entities=response.entities
				logging.info("Detected entities: "+str(entities))
			sequence_reader.readSequence(current_app._get_current_object(), json.loads(seq_data), entities)
	emit("response", response_text)


@socketio.on('play_sequence', namespace='/client')
def play_sequence(seq_name):
	"""
	Fonction appelée lorsque le client demande l'execution d'une sequence.
	"""
	seq = Sequence.query.filter_by(id=seq_name).first()
	if(seq!=None and seq.enabled):
		seq_data = seq.value
		logging.info('Executing sequence '+seq_name)
		sequence_reader.readSequence(current_app._get_current_object(), json.loads(seq_data))

@socketio.on('command', namespace='/client')
def command(label):
	"""
	Fonction appelée lorsque le client demande l'execution d'une commande simple.
	"""
	logging.info("Received command: "+label)
	sequence_reader.executeAction(current_app._get_current_object(), label)
