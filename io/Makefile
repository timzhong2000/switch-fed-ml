# path
ROOT_DIR := $(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))
BUILDDIR ?= $(ROOT_DIR)/build
OBJDIR := $(BUILDDIR)/obj

# Compiler / linker flags
CXX := g++
CXXFLAGS += -std=c++17 -fPIC
LDFLAGS += -lboost_system -lboost_program_options -lpthread -lstdc++


%.o: %.cc $(OBJDIR)
	$(CC) $(CXXFLAGS) -c $< -o $(OBJDIR)/$@ $(LDFLAGS)

$(OBJDIR):
	mkdir -p $(OBJDIR)

.PHONY: clean
clean:
	rm -rf $(OBJDIR)