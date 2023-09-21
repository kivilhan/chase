from .models import Trader, Position, Order
import pickle

def UpdateStatus():
	with open('status.pickle','rb') as f:
		status = pickle.load(f)
		f.close()

	Prime_mkI = Trader.objects.filter(title='Prime_mkI').first()
	Prime_mkI.gains = status['Gains_mkI']
	Prime_mkI.last_seen = status['Time']
	Prime_mkI.save()

	Prime_mkII = Trader.objects.filter(title='Prime_mkII').first()
	Prime_mkII.gains = status['Gains_mkII']
	Prime_mkII.last_seen = status['Time']
	Prime_mkII.save()

	ords = status['Orders_mkI']
	for ordr in ords:
		qset = Order.objects.filter(pkid=ordr)
		if len(qset) == 0:
			ordr_obj = Order(pkid=ordr,
							 symbol=ords[ordr]['Symbol'],
							 qty=ords[ordr]['Qty'],
							 side=ords[ordr]['Side'],
							 price=ords[ordr]['Price'],
							 status=ords[ordr]['Status'],
							 submit=ords[ordr]['Submit'],
							 fill=ords[ordr]['Fill'],
							 owner=Prime_mkI)
			ordr_obj.save()
		else:
			ordr_obj = qset.first()
			ordr_obj.status=ords[ordr]['Status'],
			ordr_obj.save()

	ords = status['Orders_mkII']
	for ordr in ords:
		qset = Order.objects.filter(pkid=ordr)
		if len(qset) == 0:
			ordr_obj = Order(pkid=ordr,
							 symbol=ords[ordr]['Symbol'],
							 qty=ords[ordr]['Qty'],
							 side=ords[ordr]['Side'],
							 price=ords[ordr]['Price'],
							 status=ords[ordr]['Status'],
							 submit=ords[ordr]['Submit'],
							 fill=ords[ordr]['Fill'],
							 owner=Prime_mkII)
			ordr_obj.save()
		else:
			ordr_obj = qset.first()
			ordr_obj.status=ords[ordr]['Status'],
			ordr_obj.save()

	poss = status['Pos_mkI']
	for pos in poss:
		qset = Position.objects.filter(symbol=pos)
		if len(qset) == 0:
			pos_obj = Position(symbol=pos,
							   qty=poss[pos]['Qty'],
							   value=poss[pos]['Value'],
							   gain=poss[pos]['Gain'],
							   owner=Prime_mkI)
			pos_obj.save()
		else:
			pos_obj = qset.first()
			pos_obj.qty = poss[pos]['Qty']
			pos_obj.value = poss[pos]['Value']
			pos_obj.gain = poss[pos]['Gain']
			pos_obj.save()

	for pos in Position.objects.filter(owner=Prime_mkI):
		if pos.symbol not in poss:
			pos.delete()

	poss = status['Pos_mkII']
	for pos in poss:
		qset = Position.objects.filter(symbol=pos)
		if len(qset) == 0:
			pos_obj = Position(symbol=pos,
							   qty=poss[pos]['Qty'],
							   value=poss[pos]['Value'],
							   gain=poss[pos]['Gain'],
							   owner=Prime_mkII)
			pos_obj.save()
		else:
			pos_obj = qset.first()
			pos_obj.qty = poss[pos]['Qty']
			pos_obj.value = poss[pos]['Value']
			pos_obj.gain = poss[pos]['Gain']
			pos_obj.save()

	for pos in Position.objects.filter(owner=Prime_mkII):
		if pos.symbol not in poss:
			pos.delete()