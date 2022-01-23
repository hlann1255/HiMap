from django.shortcuts import render
from .forms import WayForm

# Create your views here.

from queue import PriorityQueue
from copy import deepcopy
import docx2txt


INF = 1e9
BIAS = 2.3e3


station = []
bus_number = []

def index_view(request):

	context = {}
	read_data(context)

	return render(request, "../templates/index.html", {"bus": station})


class Node:
	def __init__(self, node, weight, bus):
		self.node = node
		self.weight = weight
		self.bus = bus


class Path(Node):
	def __init__(self, dist, node, weight, bus, num_bus):
		super().__init__(node, weight, bus)

		self.dist = dist
		self.num_bus = num_bus


	def __lt__(self, o):
		return self.dist < o.dist


def dijkstra(adj, trace, dist, s, t, max_num_bus):
	trace.update({x : [None] * (max_num_bus + 5) for x in adj.keys()})
	dist.update({x : [INF] * (max_num_bus + 5) for x in adj.keys()})

	pq = PriorityQueue()

	for u in adj.values():
		for v in u:
			if v.node == s.node:
				dist[v.node][0] = 0
				pq.put(Path(0, v.node, 0, v.bus, 0))

	while not pq.empty():
		u = pq.get()

		if u.num_bus > max_num_bus or u.dist > dist[u.node][u.num_bus]:
			continue

		if u.node == t.node:
			return u.num_bus

		for v in adj[u.node]:
			dif_bus = (u.bus != v.bus)

			if dist[v.node][u.num_bus + dif_bus] > u.dist + v.weight + dif_bus * BIAS:
				dist[v.node][u.num_bus + dif_bus] = u.dist + v.weight + dif_bus * BIAS
				trace[v.node][u.num_bus + dif_bus] = Node(u.node, u.num_bus, u.bus)

				pq.put(Path(dist[v.node][u.num_bus + dif_bus], v.node, v.weight, v.bus, u.num_bus + dif_bus))

	return 0


def read_data(adj):
	data = (docx2txt.process("static/data/Data.docx")).splitlines()

	line = 0
	while line < len(data):
		bus = data[line].strip()
		line += 2

		if bus == 'EOF':
			break

		v_node = data[line].strip()
		line += 4

		while True:
			u_node = v_node
			v_node = data[line].strip()
			if (v_node != ''): station.append(v_node)

			if v_node == '':
				line += 2
				break

			weight = int(data[line + 2])
			line += 4

			if not u_node in adj:
				adj[u_node] = []

			if not v_node in adj:
				adj[v_node] = []

			adj[u_node].append(Node(v_node, weight, bus))


def output(trace, s, t, num_bus):

	if not isinstance(trace[t.node][num_bus], Node):
		return None

	t.bus = trace[t.node][num_bus].bus

	path = t
	prev_bus = t.bus
	prev_node = t.node
	output = ''

	while (trace[path.node][num_bus] != None):
		if path.bus != prev_bus:
			output = 'Đón chuyến {:6s} từ {:30s} đến {:30s}'.format(
				prev_bus, path.node, prev_node + '.'
			) + '\n' + output
			bus_number.append(prev_bus)

			prev_bus = path.bus
			prev_node = path.node
			num_bus = path.weight

		path = trace[path.node][num_bus]

	output = 'Đón chuyến {:6s} từ {:30s} đến {:30s}'.format(
		prev_bus, path.node, prev_node + '.'
	) + '\n' + output
	bus_number.append(prev_bus)

	return output


def get_data(request):
	# if this is a POST request we need to process the form data
	if request.method == 'POST':
		# create a form instance and populate it with data from the request:
		form = WayForm(request.POST)

		if form.is_valid():
			start = form.cleaned_data["start"]
			end = form.cleaned_data["end"]
			bus_number.clear()

			adj = {}
			trace = {}
			dist = {}
			s = Node(start, 0, '')
			t = Node(end, 0, '')
			max_num_bus = 3

			read_data(adj)

			data = output(trace, s, t, dijkstra(adj, trace, dist, s, t, max_num_bus))

			if (data == None):
				data = "Không tìm được điểm đến"
			if (bus_number == None):
				bus = "Không tìm được xe bus"

			return render(request, '../templates/index.html', {"bus": station,"data": data, "bus_number": bus_number, "end": end})