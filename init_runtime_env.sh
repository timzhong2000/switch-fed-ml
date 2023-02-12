# Port0 11.11.11.1 connected to veth1
sudo ip link add name veth0 type veth peer name veth1
sudo ip link set dev veth0 up
sudo ip link set dev veth1 up
sudo ip link set veth0 mtu 9000
sudo ip link set veth1 mtu 9000
sudo sysctl net.ipv6.conf.veth0.disable_ipv6=1
sudo sysctl net.ipv6.conf.veth1.disable_ipv6=1
sudo ip addr add 11.11.11.1/16 dev veth1

# Port1 11.11.11.2 connected to veth3
sudo ip link add name veth2 type veth peer name veth3
sudo ip link set dev veth2 up
sudo ip link set dev veth3 up
sudo ip link set veth2 mtu 9000
sudo ip link set veth3 mtu 9000
sudo sysctl net.ipv6.conf.veth2.disable_ipv6=1
sudo sysctl net.ipv6.conf.veth3.disable_ipv6=1
sudo ip addr add 11.11.11.2/16 dev veth3

# Port2 11.11.11.3 connected to veth5
sudo ip link add name veth4 type veth peer name veth5
sudo ip link set dev veth4 up
sudo ip link set dev veth5 up
sudo ip link set veth4 mtu 9000
sudo ip link set veth5 mtu 9000
sudo sysctl net.ipv6.conf.veth4.disable_ipv6=1
sudo sysctl net.ipv6.conf.veth5.disable_ipv6=1
sudo ip addr add 11.11.11.3/16 dev veth5
