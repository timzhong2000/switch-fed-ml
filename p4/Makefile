CC=p4c
BUILD_DIR=switchfl.bmv2

all:
	$(CC) -b bmv2 switchfl.p4 -o $(BUILD_DIR) --p4runtime-files $(BUILD_DIR)/p4info.json

clean:
	rm -rf $(BUILD_DIR)