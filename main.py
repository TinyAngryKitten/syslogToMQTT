import os
import sys
import socketserver
import paho.mqtt.client as mqtt
import socket
import logging

HOST = "0.0.0.0"
PORT = os.getenv('PORT')
if PORT is None:
	PORT = 514
else: PORT = int(PORT)

CCHOST = os.getenv('CCHOST')
CCPORT = os.getenv('CCPORT')
if CCPORT is not None:
	CCPORT = int(CCPORT)

BROKER = os.getenv('BROKER')
BROKER_PORT = int(os.getenv('BROKER_PORT'))
BROKER_CLIENT_ID = os.getenv('BROKER_CLIENT_ID')
TOPIC = os.getenv('BROKER_TOPIC')
if TOPIC is None:
	TOPIC = '/logs/'

LOG_FILE = 'logfile.log'
logging.basicConfig(level=logging.INFO, format='%(message)s', datefmt='', filename=LOG_FILE, filemode='a')

class SyslogUDPHandler(socketserver.BaseRequestHandler):
	mqttClient = mqtt.Client(BROKER_CLIENT_ID,protocol=mqtt.MQTTv5)
	mqttClient.connect(BROKER, BROKER_PORT)

	def handle(self):
		data = bytes.decode(self.request[0].strip(), encoding="utf-8")
		logging.info(str(data))

		#send copy of message to another server
		if CCHOST is not None:
			socket.socket(socket.AF_INET, socket.SOCK_DGRAM)\
				.sendto(self.request[0].strip(), (CCHOST, CCPORT))

		if not self.mqttClient.is_connected():
			self.mqttClient.reconnect()
		self.mqttClient.publish(TOPIC+self.client_address[0], str(data))

if __name__ == "__main__":
	logging.info("Starting...")
	logging.info("Binding to 0.0.0.0:" + str(PORT))
	logging.info("connecting to Broker: "+BROKER+":"+str(BROKER_PORT)+" as "+BROKER_CLIENT_ID)

	if CCHOST is not None:
		logging.info("Forwarding messages to "+CCHOST+":"+str(CCPORT))
	else: logging.info("Messages will not be forwarded")

	try:
		server = socketserver.UDPServer((HOST,PORT), SyslogUDPHandler)
		server.serve_forever(poll_interval=0.5)
	except:
		logging.info("Unexpected error:", sys.exc_info()[0])
		raise
	logging.info("Shutting down...")
