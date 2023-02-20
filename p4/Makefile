CC=p4c
BUILD_DIR=switchfl.bmv2
BM=simple_switch_grpc

all:
	$(CC) -b bmv2 switchfl.p4 -o $(BUILD_DIR) --p4runtime-files $(BUILD_DIR)/p4info.txt

run:
	simple_switch_grpc --interface 0@veth0 --interface 1@veth2 $(BUILD_DIR)/switchfl.json --nanolog ipc:///tmp/bm-log.ipc

clean:
	rm -rf $(BUILD_DIR)