CC=g++
CCFLAGS= -Wall -g -O3 -std=c++11

all: kaufmanbroeckx rlt1 sqap

kaufmanbroeckx: kaufmanbroeckx.cc kaufmanbroeckx.h utils.h assignment.h
	$(CC) $(CCFLAGS) kaufmanbroeckx.cc -o kaufmanbroeckx

rlt1: rlt1.cc utils.h assignment.h
	$(CC) $(CCFLAGS) rlt1.cc -o rlt1

sqap: sqap.cc utils.h assignment.h
	$(CC) $(CCFLAGS) sqap.cc -o sqap

clean:
	rm  kaufmanbroeckx rlt1 sqap
