
CXX = g++

CXXFLAGS = -Wall -Wextra -std=c++11

TARGET = hello

SRCS = main.cpp hello.cpp

HDRS = hello.h utils.h

OBJS = $(SRCS:.cpp=.o)

.PHONY: all
all: $(TARGET)

$(TARGET): $(OBJS)
	$(CXX) $(CXXFLAGS) -o $@ $^

%.o: %.cpp $(HDRS)
	$(CXX) $(CXXFLAGS) -c $< -o $@

clean:
	rm -f $(OBJS) $(TARGET)

.PHONY: all clean
