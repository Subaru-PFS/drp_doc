# -pdf tells latexmk to generate PDF directly (instead of DVI).
# -pdflatex="" tells latexmk to call a specific backend with specific options.
# -use-make tells latexmk to call make for generating missing files.

# -interaction=nonstopmode keeps the pdflatex backend from stopping at a
# missing file reference and interactively asking you for an alternative.

TARGETS = 2DDRP-plan.pdf
DEPS_DIR = .deps
#  -silent 
LATEXMK = latexmk -recorder -use-make -deps \
                  -e 'warn qq(In Makefile, turn off custom dependencies\n);' \
                  -e '@cus_dep_list = ();' \
                  -e 'show_cus_dep();'

all : $(TARGETS)
$(foreach file,$(TARGETS),$(eval -include $(DEPS_DIR)/$(file)P))

$(DEPS_DIR) :
	mkdir $@
#
# Glossaries
#
%.acr : %.acn
	makeglossaries $*.acn
%.gls : %.glo
	makeglossaries $*.glo

%.pdf : %.tex
	@ mkdir -p $(DEPS_DIR)
	@ echo Running latexmk
	@ $(LATEXMK) -pdf -pdflatex="pdflatex -interaction=nonstopmode" \
		-deps-out=$(DEPS_DIR)/$@P $< | \
		grep -v ' restricted \\write18 enabled.'

clean:
	latexmk -CA
	$(RM) -r `biber --cache`
	$(RM) *.acn *.acr *.alg *.bbl *.glg *.glo *.gls *.xdy *.run.xml
	$(RM) *~
	$(RM) -r $(DEPS_DIR)
