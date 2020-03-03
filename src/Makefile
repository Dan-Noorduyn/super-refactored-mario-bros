DOX=doxygen
DC=config
LX=pdflatex

all:
	make pdf
doc:
	$(DOX) $(DC)
pdf: doc
	cd latex && $(MAKE)
	mv latex/refman.pdf ../Doc/Design/MIS/MIS.pdf
clean:
	rm -r latex html *.log