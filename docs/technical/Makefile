# Minimal makefile for Sphinx documentation

SPHINXOPTS    ?=
SPHINXBUILD   ?= ../../.venv/bin/sphinx-build
SPHINXAUTO    ?= ../../.venv/bin/sphinx-autobuild
SOURCEDIR     = .
BUILDDIR      = _build
DOCS_PORT     ?= 8400

help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

clean:
	rm -rf "$(BUILDDIR)"

# Live-reload server: rebuilds on save and refreshes the browser.
serve:
	@$(SPHINXAUTO) "$(SOURCEDIR)" "$(BUILDDIR)/html" --port $(DOCS_PORT) --open-browser $(SPHINXOPTS)

.PHONY: help clean serve Makefile

%: Makefile
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
