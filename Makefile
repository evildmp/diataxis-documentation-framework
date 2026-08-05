SPHINXOPTS    =
SPHINXBUILD   = sphinx-build
SPHINXPROJ    = Diátaxis

SOURCEDIR     = source
BUILDDIR      = _build
HTMLDIR       = $(BUILDDIR)/html
GETTEXTDIR    = $(BUILDDIR)/gettext
SPELLINGDIR   = $(BUILDDIR)/spelling

TRANSLATIONSDIR = translation
TRANSLATIONLANGUAGES = fr it pt_BR de zh_CN pl ja

VENV = env/bin/activate
PORT = 8090

# Put it first so that "make" without argument is like "make help".
help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

install:
	@echo "... setting up virtualenv"
	python3 -m venv env
	. $(VENV); pip install --upgrade -r requirements.txt
	@echo "\n" \
	  "--------------------------------------------------------------- \n" \
      "* watch, build and serve the documentation: make run \n" \
	  "* check spelling: make spelling \n" \
	  "\n" \
      "enchant must be installed in order for pyenchant (and therefore \n" \
	  "spelling checks) to work. \n" \
	  "--------------------------------------------------------------- \n"

clean:
	-rm -rf $(BUILDDIR)/*

run:
	. $(VENV); sphinx-autobuild $(ALLSPHINXOPTS) --ignore ".git/*" --ignore "*.scss" $(SOURCEDIR) -b dirhtml -a $(HTMLDIR) --host 127.0.0.1 --port $(PORT)

test:
	. $(VENV); $(SPHINXBUILD) -b html $(SOURCEDIR) $(HTMLDIR)

html:
	. $(VENV); $(SPHINXBUILD) -b dirhtml -D language=en $(SOURCEDIR) $(HTMLDIR)

html-fr:
	. $(VENV); $(SPHINXBUILD) -b dirhtml -D language=fr $(SOURCEDIR) $(HTMLDIR)/fr

html-pt_BR:
	. $(VENV); $(SPHINXBUILD) -b dirhtml -D language=pt_BR $(SOURCEDIR) $(HTMLDIR)/pt_BR

html-it:
	. $(VENV); $(SPHINXBUILD) -b dirhtml -D language=it $(SOURCEDIR) $(HTMLDIR)/it

html-pl:
	. $(VENV); $(SPHINXBUILD) -b dirhtml -D language=pl $(SOURCEDIR) $(HTMLDIR)/pl

html-ja:
	. $(VENV); $(SPHINXBUILD) -b dirhtml -D language=ja $(SOURCEDIR) $(HTMLDIR)/ja

html-all: html html-pl

run-all: html-all run

gettext:
	. $(VENV); $(SPHINXBUILD) -M gettext "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

update-po-files:
	. $(VENV); sphinx-intl update -p $(GETTEXTDIR) -d $(TRANSLATIONSDIR) $(foreach lang,$(TRANSLATIONLANGUAGES),-l $(lang))

spelling:
	. $(VENV); $(SPHINXBUILD) -b spelling $(ALLSPHINXOPTS) $(SOURCEDIR) $(SPELLINGDIR)
	@echo
	@echo "Check finished. Wrong words can be found in " \
		"$(SPELLINGDIR)/output.txt."


.PHONY: help install clean run html html-fr html-it html-pt_BR html-pl html-ja html-all run-all gettext update-po-files spelling quickstart Makefile

# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
%: Makefile
	. $(VENV); @$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
