import subprocess

def run(cmd):
    subprocess.run(cmd, shell=True)

def init():
    # 清理原有的队列和分类
    run("tc qdisc del dev lo root")
    run("iptables -t mangle -F")
    # 创建htb队列
    run("tc qdisc add dev lo root handle 1: htb default 1")

def limit_speed(group: str, rx_port: int, tx_port: int, speed: int):
    run("tc class add dev lo parent 1: classid 1:%s htb rate %dmbit ceil %dmbit" %
        (group, speed, speed))
    run("tc filter add dev lo protocol ip parent 1: prio 0 handle %s fw flowid 1:%s" % (
        group, group))
    if rx_port is not None:
        run("iptables -t mangle -A OUTPUT -p udp --dport=%d -j MARK --set-mark=%s" %
        (rx_port, group))
        run("iptables -t mangle -A OUTPUT -p tcp --dport=%d -j MARK --set-mark=%s" %
        (rx_port, group))
        run("iptables -t mangle -A OUTPUT -p tcp --sport=%d -j MARK --set-mark=%s" %
        (rx_port, group))
    if tx_port is not None:
        run("iptables -t mangle -A OUTPUT -p udp --sport=%d -j MARK --set-mark=%s" %
        (tx_port, group))
    
def init_node(node_id: int, rx_port: int, tx_port: int, speed: int):
    limit_speed('1%02d'%node_id, rx_port, tx_port, speed)



def throttle(node_speed: int, node_num: int, scale: int = 1):
    # 限速策略
    # 1xx：节点
    # 2: 参数服务器
    init()
    limit_speed('2', 50000, None, node_speed * scale) # 参数服务器限速 node_speed M
    limit_speed('1', None, None, node_num * node_speed)
    for i in range(node_num):
        init_node(i + 1, 50003 + i * 3, 50004 + i * 3, node_speed)
