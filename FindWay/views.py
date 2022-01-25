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
    # trả phần dữ liệu đã xử lý (các trạm) về file html để hiển thị mặc định


class Node:
    def __init__(self, node, weight, bus):
        self.node = node
        self.weight = weight
        self.bus = bus
# khởi tạo class Node lưu thông tin 1 đỉnh


class Path(Node):
    def __init__(self, dist, node, weight, bus, num_bus):
        super().__init__(node, weight, bus)

        self.dist = dist
        self.num_bus = num_bus
    # khởi tạo class Path để lưu thông tin 1 trạng thái

    def __lt__(self, o):
        return self.dist < o.dist
    # quy định cách so sánh self và o


def dijkstra(adj, trace, dist, s, t, max_num_bus):
    trace.update({x : [None] * (max_num_bus + 5) for x in adj.keys()})
    dist.update({x : [INF] * (max_num_bus + 5) for x in adj.keys()})
    # gán giá trị cho tất cả phần tử trong trace là None và trong dist là INF
    # để dễ dàng cập nhật trong thuật toán

    pq = PriorityQueue()

    for u in adj.values():
        for v in u:
            if v.node == s.node:
                dist[v.node][0] = 0
                pq.put(Path(0, v.node, 0, v.bus, 0))
    # duyệt tất cả chuyến xe có chứa trạm bắt đầu để đưa vào priority queue

    while not pq.empty():
    # xét từng trạng thái trong priority queue
        u = pq.get()

        if u.num_bus > max_num_bus or u.dist > dist[u.node][u.num_bus]:
        # nếu số lần đổi tuyến đã vượt quá quy định
        # hoặc khoảng cách đang xét lớn hơn khoảng cách tối ưu hiện tại
            continue
            # thì bỏ qua trạng thái này
        
        if u.node == t.node:
        # nếu đã tìm được đường đi đến đích tối ưu
            return u.num_bus
            # thì trả về số lần đổi chuyến để truy vết ở hàm output

        # Đang xét trạng thái u: ở đỉnh u.node và đã đổi xe u.num_bus lần
        # Xét đỉnh v.node kề với u.node để xem có thể tối ưu nó bằng trạng thái u hay không:
        for v in adj[u.node]:
            dif_bus = (u.bus != v.bus)
            # xét xem v.bus và u.bus có khác nhau ko (có phải đổi chuyến ko)
            # giống thì dif_bus = 0, ngược lại = 1

            # dist từ s đến v = từ s đến u + từ u đến v = u.dist + v.weight + dif_bus * BIAS
            # giải thích BIAS
            # num_bus từ s đến v = từ s đến u + từ u đến v = u.num_bus + dif_bus
            if dist[v.node][u.num_bus + dif_bus] > u.dist + v.weight + dif_bus * BIAS:
            # nếu đi từ s đến v thông qua u tối ưu hơn cách đi từ s đến v hiện tại
                dist[v.node][u.num_bus + dif_bus] = u.dist + v.weight + dif_bus * BIAS
                trace[v.node][u.num_bus + dif_bus] = Node(u.node, u.num_bus, u.bus)
                #thì cập nhật khoảng cách bằng cách đi tối ưu và lưu vết cách đi

                pq.put(Path(dist[v.node][u.num_bus + dif_bus], v.node, v.weight, v.bus, u.num_bus + dif_bus))
                #và thêm trạng thái mới đó vào pq

    return 0
    # nếu không tìm được cách đi thì trả số lần đổi chuyến về 0


def read_data(adj):
# hàm đọc dữ liệu
    global station
    data = (docx2txt.process("static/data/Data.docx")).splitlines()

    line = 0
    while line < len(data):
        bus = data[line].strip()
        line += 2

        if bus == 'EOF':
            break
        # nếu đã đọc đến cuối file dữ liệu thì thoát

        v_node = data[line].strip()
        line += 4

        while True:
            u_node = v_node
            v_node = data[line].strip()
            # xét 2 đỉnh kề nhau

            if (v_node != ''): station.append(v_node)
            # lưu lại các trạm có trong file dữ liệu để người dùng chọn

            if v_node == '':
                line += 2
                break

            weight = int(data[line + 2])
            line += 4

            if not u_node in adj:
                adj[u_node] = []

            if not v_node in adj:
                adj[v_node] = []
            # thêm u.node, v.node vào danh sách kề

            adj[u_node].append(Node(v_node, weight, bus))
            #Danh sách kề lưu các đỉnh kề nhau

    station = list(set(station))
    station.sort()
    # tránh lặp lại và sắp xếp các trạm để dễ dàng cho người dùng chọn

def output(trace, s, t, num_bus):
    global bus_number
    if not isinstance(trace[t.node][num_bus], Node): 
    # Nếu trace ở trạng thái None (không có đường đi đến)
        return None
        # thì trả hàm về None để thông báo cho người sử dụng

    t.bus = trace[t.node][num_bus].bus

    path = t
    prev_bus = t.bus
    prev_node = t.node
    output = ''

    while (trace[path.node][num_bus] != None):
        if path.bus != prev_bus:
            # xét 2 trạm kế bên nhau nếu khác chuyến xe thì in ra
            output = 'Đón chuyến {:6s} từ {:30s} đến {:30s}'.format(
                prev_bus, path.node, prev_node + '.'
            ) + '\n' + output
            bus_number.append(prev_bus)
            # lưu lại các chuyến xe cần đi

            prev_bus = path.bus
            prev_node = path.node
            num_bus = path.weight
            # lưu trạm hiện tại về trạm trước để xét tiếp

        path = trace[path.node][num_bus]

    output = 'Đón chuyến {:6s} từ {:30s} đến {:30s}'.format(
        prev_bus, path.node, prev_node + '.'
    ) + '\n' + output
    bus_number.append(prev_bus)

    return output


def get_data(request):
    # xử lý dữ liệu biểu mẫu khi có yêu cầu POST
    if request.method == 'POST':
        # tạo và điền một phiên bản form với dữ liệu từ yêu cầu:
        form = WayForm(request.POST)
        global bus_number
        if form.is_valid():
            start = form.cleaned_data["start"]
            end = form.cleaned_data["end"]
            # đọc điểm bắt đầu và đích đến

            bus_number.clear()
            adj = {}
            trace = {}
            dist = {}
            s = Node(start, 0, '')
            t = Node(end, 0, '')
            max_num_bus = 3
            # khởi tạo

            read_data(adj)
            # đọc dữ liệu

            data = output(trace, s, t, dijkstra(adj, trace, dist, s, t, max_num_bus))
            # data trả về là cách đi từ start đến end

            bus_number = list(set(bus_number))
            
            if (data == None):
                data = "Không tìm được đường đi"
            if (len(bus_number) == 0): 
                bus_number.append("Không tìm được xe bus")

            return render(request, '../templates/index.html', {"bus": station,"data": data, "bus_number": bus_number, "end": end})
            # trả các dữ liệu đã xử lý về file html để hiển thị