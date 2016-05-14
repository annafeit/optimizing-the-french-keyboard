Quick Start Guide

$ make
g++ -Wall -g -O3 -std=c++11 kaufmanbroeckx.cc -o kaufmanbroeckx
g++ -Wall -g -O3 -std=c++11 rlt1.cc -o rlt1
g++ -Wall -g -O3 -std=c++11 sqap.cc -o sqap
$ ./kaufmanbroeckx < reformulation_input.txt > reformulation.lp

'make' compiles three generators that convert input data (see 
http://resources.mpi-inf.mpg.de/keyboardoptimization/ for downloads, e.g. 
input-26-S.txt for the case of 26 letters and keys with a stylus input model) to 
LP-files according to the corresponding formulations.

 ./kaufmanbroeckx creates the reformualtion from the given input file and saves it as the given output file. 
