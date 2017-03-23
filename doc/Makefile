LATEX    = latex
BIBTEX   = bibtex
DVIPS    = dvips

default: proc

proc:
	latex proc
	bibtex proc
	latex proc
	latex proc
	dvipdf -sPAPERSIZE=a4 -dPDFSETTINGS=/prepress proc
	rm -f *.aux *.log *.bbl *.blg *.brf *.cb *.ind *.idx *.ilg *.inx *.dvi *.toc *.out *.lof *.lot *~ ~*
	open -a Preview proc.pdf


clean:
	rm -f *.aux *.log *.bbl *.blg *.brf *.cb *.ind *.idx *.ilg *.inx *.dvi *.toc *.out *.lof *.lot *~ ~* proc.pdf

#
# standard Latex targets
#

%.dvi:	%.tex 
	$(LATEX) $<

%.bbl:	%.tex *.bib
	$(LATEX) $*
	$(BIBTEX) $*

%.ps:	%.dvi
	$(DVIPS) $< -o $@

%.pdf:	%.tex
	$(PDFLATEX) $<


