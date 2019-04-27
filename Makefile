PROGRAM := filter

SRCS := $(wildcard *.c)
OBJS := $(SRCS:.c=.o)

$(PROGRAM): $(OBJS)
	gcc -o $@ $(OBJS)
	
%.o:%.c
	gcc -c $<
