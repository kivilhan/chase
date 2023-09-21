import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "chase_live.settings")
import django
django.setup()
from deployment.models import Trader, Order, Position

traders = Trader.objects.all()
for trader in traders:
    print(trader.description)

from kafka import KafkaConsumer
from json import loads
consumer = KafkaConsumer('chase_data3', bootstrap_servers='localhost:9092')
ins = []
for msg in consumer:
    ins.append(loads(msg.value))
    
    
    # print (msg)