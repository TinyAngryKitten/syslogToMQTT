# Syslog to MQTT
A very simple syslog sever which will broadcast all received UDP-messages to an mqtt server.
It can also forward a copy of the syslog message to another syslog server.
Configuration is done with environment variables:

- PORT: The port to which the server will bind to
- CCHOST: Address to the host which will receive the message copies
- CCHOST_PORT: The port which the CCHOST is listening at
- BROKER: MQTT broker address
- BROKER_PORT: MQTT broker port
- BROKER_CLIENT_ID: Client id used to connec to the mqtt broker