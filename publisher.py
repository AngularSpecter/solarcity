import solar
import paho.mqtt.client as mqtt
import secrets
import json
import time

mqtt_topic = 'home/electricity/solar/stats'

# INIT solar city powerAPI connection
print("Starting SolarCity COnnector") 
sc = solar.SolarCity( secrets.GUID, secrets.token )

# Setup MQTT
print("Setting up MQTT")
mqtt_client = mqtt.Client()
mqtt_client.connect( secrets.mqtt_broker )
mqtt_client.loop_start()

while True:
  print("Polling the API")
  #Poll the API every minute
  #{'energy': 6.91, 'cost': 1.66760412}
  #{'energy': 57.39, 'cost': 13.85004348}
  #{'alerts': []}

  today = sc.get_today_total()
  month = sc.get_month_total()
  alerts = sc.get_alerts()

  today_topic = mqtt_topic  + '/today'
  month_topic = mqtt_topic  + '/month'
  alerts_topic = mqtt_topic + '/alerts'

  today_jstring = json.dumps( today )
  month_jstring = json.dumps( month )

  print( "publishing " + today_topic + " : " + today_jstring )
  print( "publishing " + month_topic + " : " + month_jstring )

  mqtt_client.publish( today_topic, today_jstring )
  mqtt_client.publish( month_topic, today_jstring )
  
  time.sleep( 60 )
