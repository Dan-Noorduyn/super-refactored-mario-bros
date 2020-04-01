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
game:
	python3 -m venv ./env
	./env/bin/python3 -m pip install pygame==2.0.0.dev6 scipy pyinstaller
	cd ./mariopy && ../env/bin/pyinstaller -F ./main.py
doc:
	$(DOX) $(DC)
pdf: doc
	cd latex && $(MAKE)
	mv latex/refman.pdf ../Doc/Design/MIS/MIS.pdf
cleangame:
	rm -r ./env ./mariopy/dist ./mariopy/build ./mariopy/main.spec
cleandoc:
	rm -r latex html *.log
clean: cleangame cleandoc