# **C.I.P.H.E.R: Control Interface for Programmable Homemade Entertainment Robot**

![alt text](https://raw.githubusercontent.com/valorun/CIPHER/master/docs/capture.png)
Interface de contrôle robotique C.I.P.H.E.R. Il s'agit d'une interface web réalisée en HTML/Js permettant une connexion à un raspberry via un serveur Python Flask. En outre, l'utilisateur peut ordonner l'exécution de commandes sur les raspberries inter-connectés, tel que l'activation de relais ou de servo-moteurs.

## Fonctionnalités

- Gestions d'actions primaires
    - Activation de relais
    - Activation de servomoteurs
    - Lancement de son (sur le navigateur ou sur le serveur)
- Création de séquences sous forme de graph
- Intégration de la synthèse vocale MaryTTS (<http://mary.dfki.de/>)
- Panneau de côntrole personnalisable
- Possibilité d'ajouter ses propres actions ou plugins

## Installation

Téléchargez et décompressez l'archive de C.I.P.H.E.R sur le serveur à l'emplacement désiré.
Pour une installation automatique, exécutez le script ```setup.sh``` disponible à la racine du dossier.
Le client (disponible à l'adresse suivante: <https://github.com/valorun/CIPHER-raspberry-client>) doit être ensuite installé sur tout les raspberries devant être connectés.

### Pré-requis

- Python3 sur le raspberry serveur, et sur les raspberries connectés

### Installation manuelle

Dans le cadre de notre exemple, l'application est décompressée dans le dossier ```/home/pi```.
La communication entre le serveur et les client se faisant via le protocole MQTT, il est nécessaire d'installer un broker.
Nous utilisons ici mosquitto: ```sudo apt install```
Pour mettre en route le serveur au démarrage du raspberry, plusieurs méthodes existent.
Dans notre cas, la ligne ```nohup /home/pi/CIPHER/app.py``` est ajoutée avant le 'exit 0' du fichier ```etc/rc.local```.

## Utilisation

Une fois correctement installé et lancé, le serveur peut ensuite être accédé depuis l'adresse du raspberry dans un navigateur avec le port 5000. Sur un réseau local l'URL sera sous le format suivant :```https://192.168.0.X:5000```.

## Bibliothèques utilisées

### Python

- flask (<http://flask.pocoo.org/>)
- flask-SocketIO (<https://flask-socketio.readthedocs.io/en/latest/>)
- flask-SQLAlchemy (<http://flask-sqlalchemy.pocoo.org/2.3/>)
- flask-MQTT (<https://flask-mqtt.readthedocs.io/en/latest/>)

### JavaScript

- muuri (<https://github.com/haltu/muuri>)
- socket.io (<https://github.com/socketio/socket.io>)
- vis.js (<https://github.com/almende/vis/tree/develop>)
