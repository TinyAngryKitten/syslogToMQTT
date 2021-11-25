import os
import sys
import socketserver
import paho.mqtt.client as mqtt
import socket
import logging
import requests
import re

HOST = "0.0.0.0"
PORT = os.getenv('PORT')
if PORT is None:
    PORT = 514
else:
    PORT = int(PORT)

HTTP_URL = os.getenv('HTTP_URL')

CCHOST = os.getenv('CCHOST')
CCPORT = os.getenv('CCPORT')
if CCPORT is not None:
    CCPORT = int(CCPORT)

BROKER = os.getenv('BROKER')
BROKER_PORT = int("1883" if os.getenv('BROKER_PORT') is None else os.getenv('BROKER_PORT'))
BROKER_CLIENT_ID = os.getenv('BROKER_CLIENT_ID')
TOPIC = os.getenv('BROKER_TOPIC')
if TOPIC is None:
    TOPIC = '/logs/'
if BROKER is None:
    BROKER = '192.168.50.3'
if BROKER_CLIENT_ID is None:
    BROKER_CLIENT_ID = "Syslog forwarding agent"

LOG_FILE = 'logfile.log'
logging.basicConfig(level=logging.INFO, format='%(message)s', datefmt='', filename=LOG_FILE, filemode='a')


class SyslogUDPHandler(socketserver.BaseRequestHandler):
    def handle(self):
        data = bytes.decode(self.request[0].strip(), encoding="utf-8")

        name = ""
        message = ""
        try:
            search = re.search('<\\d+>\\w+ \\d+ \\d+:\\d+:\\d+ ([\\w_\\-.]+)', str(data))
            name = search.group(1)
            message = search.group(2)
        except:
            print("no data available")

        msgJson = {
            "message": message if message is not "" and name is not "" else str(data),
            "service": name,
            "host": self.client_address[0]
        }

        logging.info(msgJson)

        if HTTP_URL is not None:
            requests.post(HTTP_URL, json=msgJson)

        # send copy of message to another server
        if CCHOST is not None:
            socket.socket(socket.AF_INET, socket.SOCK_DGRAM) \
                .sendto(self.request[0].strip(), (CCHOST, CCPORT))


if __name__ == "__main__":
    logging.info("Starting...")
    logging.info("Binding to 0.0.0.0:" + str(PORT))
    logging.info("connecting to Broker: " + BROKER + ":" + str(BROKER_PORT) + " as " + BROKER_CLIENT_ID)

    if CCHOST is not None:
        logging.info("Forwarding messages to " + CCHOST + ":" + str(CCPORT))
    else:
        logging.info("Messages will not be forwarded")

    if HTTP_URL is not None:
        logging.info("Will forward messages to http endpoint: " + HTTP_URL)
    else:
        logging.info("Will not forward messages to http endpoint")

    try:
        server = socketserver.UDPServer((HOST, PORT), SyslogUDPHandler)
        server.serve_forever(poll_interval=0.5)
    except:
        logging.info("Unexpected error:", sys.exc_info()[0])
        raise
    logging.info("Shutting down...")
