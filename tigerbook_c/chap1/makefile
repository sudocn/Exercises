CFLAGS := -I. -g
H_FILES := slp.h util.h table.h log.h
a.out: log.o table.o main.o prog1.o slp.o util.o 
	cc -g $^ 

main.o: ${H_FILES}
log.o: log.h list.h
table.o: table.h util.h
prog1.o: slp.h util.h
slp.o: slp.h util.h
util.o:  util.h

%.o: %.c
	cc ${CFLAGS} -c $< 

clean: 
	rm -f a.out util.o prog1.o slp.o main.o
