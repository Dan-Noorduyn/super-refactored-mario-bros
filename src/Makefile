DOX=doxygen
DC=config
LX=pdflatex

all:
	make pdf
doc:
	$(DOX) $(DC)
pdf: doc
	cd latex && $(MAKE)
clean:
	rm -r latex html *.log