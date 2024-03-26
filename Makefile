# Utilities for the project
.PHONY: help init unittest verilog verilog-dbg apidoc html docs clean clean-docs

# Help message
help:
	@echo "Project Make"
	@echo "Please use `make target` where target is one of:"
	@echo "    init           : Initialize the project and create empty folders."
	@echo "    unittest       : Run unit tests for the designs."
	@echo "    verilog        : Generate a Verilog file for the top module."
	@echo "    verilog-dbg    : Generate a Verilog file with source information included."
	@echo "    docs           : Generate documentation using Sphinx."
	@echo "    clean          : Remove generated Verilog files, waveform files, and documentation."
	@echo "    clean-docs     : Remove only the generated documentation files."

# Initialize project (Run ONCE)
init:
	mkdir -p ./hw/gen
	mkdir -p ./tests/waveform
	mkdir -p ./docs/source/_static
	mkdir -p ./docs/source/apidoc

# Unit tests
unittest:
	python -m unittest discover -t . -s tests -v

# Verilog generation
verilog:
	python -m hw.Lfsr.Lfsr --no-src

verilog-dbg:
	python -m hw.Lfsr.Lfsr

# Doc gen
apidoc:
	sphinx-apidoc -f -o ./docs/source/apidoc ./hw/

html:
	$(MAKE) -C ./docs/ html

# Sphinx documentation build
docs: apidoc html

# Clean up (Run as needed)
clean:
	rm -rf ./hw/gen/*
	rm -rf ./tests/waveform/*
	rm -rf ./docs/source/apidoc/*

clean-docs:
	$(MAKE) -C ./docs/ clean
