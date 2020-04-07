DOX=doxygen
DC=config
LX=pdflatex
ifeq ($(OS),Windows_NT)
    EXT := .exe
else
    EXT := 
endif

all:
	make game
	make run
game:
	python3 -m venv ./env
	./env/bin/python3 -m pip install pygame==2.0.0.dev6 scipy
run:
	./env/bin/python3 ./main.py
doc:
	$(DOX) $(DC)
pdf: doc
	cd latex && $(MAKE)
	mv latex/refman.pdf ../../Doc/Design/MIS/MIS.pdf
cleangame:
	rm -r ./env
cleandoc:
	rm -r latex html *.log
clean: cleangame cleandoc