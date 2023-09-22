from django.shortcuts import render, get_object_or_404
from .models import Trader, Position, Order
from django.views.generic import ListView
from .models import Trader, Position, Order
from .funcs import UpdateStatus

def home(request):
	UpdateStatus()
	context = {'post': Trader.objects.all()}
	return render(request, 'deployment/home.html', context)

class TraderListView(ListView):
	model = Trader
	template_name = 'deployment/home.html'
	context_object_name = 'traders'
	ordering = ['title']
	paginate_by = 10

	def get(self, request, *args, **kwargs):
		UpdateStatus()
		return super().get(request, *args, **kwargs)

class TraderPosListView(ListView):
	model = Position
	template_name = 'deployment/trader_pos.html'
	context_object_name = 'positions'
	paginate_by = 10

	def get_queryset(self):
		trader = get_object_or_404(Trader, title=self.kwargs.get('title'))
		return Position.objects.filter(owner=trader).order_by('symbol')


class TraderOrderListView(ListView):
	model = Order
	template_name = 'deployment/trader_orders.html'
	context_object_name = 'orders'
	paginate_by = 10

	def get_queryset(self):
		trader = get_object_or_404(Trader, title=self.kwargs.get('title'))
		return Order.objects.filter(owner=trader).order_by('fill')