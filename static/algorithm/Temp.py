from queue import PriorityQueue
from copy import deepcopy
import docx2txt 


INF = 1e9
BIAS = 1000


class Node:
	def __init__(self, node, weight, bus):
		self.node = node
		self.weight = weight
		self.bus = bus


class Path(Node):
	def __init__(self, dist, node, weight, bus):
		super().__init__(node, weight, bus)

		self.dist = dist


	def __lt__(self, o):
		return self.dist < o.dist


def dijkstra(adj, trace, dist, s, t):
	trace.update({x : None for x in adj.keys()})
	dist.update({x : INF for x in adj.keys()})

	pq = PriorityQueue()

	for u in adj.values():
		for v in u:
			if v.node == s.node:
				dist[v.node] = 0
				pq.put(Path(0, v.node, 0, v.bus))

	while not pq.empty():
		u = pq.get()

		if u.dist > dist[u.node]:
			continue

		if u.node == t.node:
			break

		for v in adj[u.node]:
			if dist[v.node] > dist[u.node] + v.weight + (u.bus != v.bus) * BIAS:
				dist[v.node] = dist[u.node] + v.weight + (u.bus != v.bus) * BIAS
				trace[v.node] = Node(u.node, u.weight, u.bus)

				pq.put(Path(dist[v.node], v.node, v.weight, v.bus))


def read_data(adj):
	data = (docx2txt.process('../data/Data.docx')).splitlines()

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


def output(trace, s, t):
	t.bus = trace[t.node].bus

	path = t
	prev_bus = t.bus
	prev_node = t.node
	output = ''

	while (trace[path.node] != None):
		if path.bus != prev_bus:
			output = 'Take bus {:6s} from {:30s} to {:30s}'.format(
				prev_bus, path.node, prev_node + '.'
			) + '\n' + output

			prev_bus = path.bus
			prev_node = path.node

		path = trace[path.node]

	output = 'Take bus {:6s} from {:30s} to {:30s}'.format(
		prev_bus, path.node, prev_node + '.'
	) + '\n' + output

	print(output)


def main():
	adj = {}
	trace = {}
	dist = {}
	s = Node('TRẠM XĂNG DẦU', 0, '')
	t = Node('THẢO NGUYÊN', 0, '')

	read_data(adj)

	dijkstra(adj, trace, dist, s, t)

	output(trace, s, t)


main()