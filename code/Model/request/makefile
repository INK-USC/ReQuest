CC = g++
CFLAGS = -lm -pthread -Ofast -march=native -Wall -funroll-loops -Wno-unused-result -lgsl -lm -lgslcblas
INCLUDES = -I/usr/include -I../eigen-3.2.5
LIBS = -L/usr/lib/x86_64-linux-gnu

request: ransampl.o hplelib.o request.o
	$(CC) $(CFLAGS) -o request ransampl.o hplelib.o request.o $(INCLUDES) $(LIBS) -lgsl -lm -lgslcblas
ransampl.o : ransampl.c
	$(CC) $(CFLAGS) -c ransampl.c $(INCLUDES) $(LIBS) -lgsl -lm -lgslcblas

hplelib.o : hplelib.cpp ransampl.h
	$(CC) $(CFLAGS) -c hplelib.cpp $(INCLUDES) $(LIBS) -lgsl -lm -lgslcblas

request.o retype-emtype.o: request.cpp hplelib.o
	$(CC) $(CFLAGS) -c request.cpp $(INCLUDES) $(LIBS) -lgsl -lm -lgslcblas
clean :
	rm -rf *.o request
