# util for the project
.PHONY: help
.PHONY: init-folders unittest verilog verilog-dbg
.PHONY: apidoc html docs clean clean-docs

help:
	@printf 'Project Make\n'
	@printf 'Please use `make target' where target is one of\n'
	@printf '    init           to init the project, create some empty folders\n'
	@printf '    unittest       to run the unit test\n'
	@printf '    verilog        to generate verilog file for the top module\n'
	@printf '    verilog-dbg    to generate verilog file for the top module, with src info\n'
	@printf '    docs           to generate docs for the project\n'
	@printf '    clean          to clean the generated verilogs and docs\n'
	@printf '    clean-docs     to clean the generated docs\n'

# Run ONCE
# Make empty folders:
init:
	mkdir -p ./hw/gen
	mkdir -p ./tests/waveform
	mkdir -p ./docs/source/_static

# Tests
unittest:
	python -m unittest discover -t . -s tests -v

# Verilog gen
verilog:
	python -m hw.project_name.Top --no-src

verilog-dbg:
	python -m hw.project_name.Top

# Doc gen
apidoc:
	sphinx-apidoc -f -e -o ./docs/source/apidoc ./hw/

html:
	$(MAKE) -C ./docs/ html

docs: apidoc html

clean:
	rm -f ./hw/gen/*
	rm -f ./tests/waveform/*
	rm -f ./docs/source/_static/*

clean-docs:
	$(MAKE) -C ./docs/ clean
