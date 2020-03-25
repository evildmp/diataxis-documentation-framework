# You can set these variables from the command line.
SPHINXOPTS    =
SPHINXBUILD   = sphinx-build
SPHINXPROJ    = DocumentationSystem
SOURCEDIR     = .
BUILDDIR      = _build

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
	-rm -rf _build/*

run:
	. $(VENV); sphinx-autobuild $(ALLSPHINXOPTS) --ignore ".git/*" --ignore "*.scss" . -b dirhtml -a _build/html --host 0.0.0.0 --port $(PORT)

test:
	. $(VENV); $(SPHINXBUILD) -b html . _build/html

html:
	. $(VENV); $(SPHINXBUILD) -b dirhtml . _build/html

spelling:
	. $(VENV); $(SPHINXBUILD) -b spelling $(ALLSPHINXOPTS) . _build/spelling
	@echo
	@echo "Check finished. Wrong words can be found in " \
		"_build/spelling/output.txt."

quickstart:
	. $(VENV); sphinx-quickstart

.PHONY: help install clean run Makefile

# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
%: Makefile
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
