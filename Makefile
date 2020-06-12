default: runcontainer

runcontainer: venv install.R
	$(VENV)/repo2docker --editable .
.PHONY: runcontainer

clean: clean-venv
	rm -r .venv/
	rm agile-2020-papers.html

# https://github.com/sio/Makefile.venv
include Makefile.venv
