from switch import Switch
from node import Node
from group import Group

mock_switch = Switch("127.0.0.1", 30000, 9, debug=True)
node1 = Node(1, "127.0.0.1", 50003, 50004, 1)
ps = Node(10, "127.0.0.1", 50000, 50001, 0)
group = Group(1, ps)
group.addNode(node1)

mock_switch.nodes[node1.id] = node1
mock_switch.nodes[ps.id] = ps
mock_switch.groups[group.id] = group

mock_switch.start()
