# Makefile for WebTics Blackjack Server
# Supports MinGW on Windows and potentially cross-compilation

CXX = g++
CXXFLAGS = -std=c++11 -Wall -I../../inc
LDFLAGS = -lwinhttp
TARGET = BlackjackServer.exe
SOURCES = BlackjackServer.cpp ../../src/WebTics.cpp
HEADERS = BlackjackEvents.h ../../inc/WebTics.h ../../inc/WebTicsDefines.h

# Default target
all: $(TARGET)

# Build the blackjack server
$(TARGET): $(SOURCES) $(HEADERS)
	$(CXX) $(CXXFLAGS) -o $(TARGET) $(SOURCES) $(LDFLAGS)
	@echo "Build complete! Run with: ./$(TARGET)"

# Clean build artifacts
clean:
	rm -f $(TARGET) *.o

# Rebuild from scratch
rebuild: clean all

# Run the server
run: $(TARGET)
	./$(TARGET)

# Help target
help:
	@echo "WebTics Blackjack Server - Makefile"
	@echo ""
	@echo "Available targets:"
	@echo "  all      - Build the blackjack server (default)"
	@echo "  clean    - Remove build artifacts"
	@echo "  rebuild  - Clean and rebuild from scratch"
	@echo "  run      - Build and run the server"
	@echo "  help     - Show this help message"
	@echo ""
	@echo "Requirements:"
	@echo "  - MinGW g++ compiler"
	@echo "  - Windows OS (uses WinHTTP library)"
	@echo ""
	@echo "Usage:"
	@echo "  make              # Build the server"
	@echo "  make run          # Build and run"
	@echo "  make clean        # Clean build files"

.PHONY: all clean rebuild run help
