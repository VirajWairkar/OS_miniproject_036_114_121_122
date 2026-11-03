CXX = g++
CXXFLAGS = -std=c++17 -Wall -Wextra -O2
all: build/os_pipeline
build/os_pipeline: src/os_pipeline.cpp
	mkdir -p build
	$(CXX) $(CXXFLAGS) $< -o $@
run: all
	bash scripts/run.sh
check: all
	bash tests/test_pipeline.sh
clean:
	rm -f build/os_pipeline
.PHONY: all run check clean
