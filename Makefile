SHELL = /bin/bash

define PROJECT_HELP_MSG
Usage:\n
  make help                   show this message\n
  make clean                  remove intermediate files (see CLEANUP)\n
  \n
  make ${VENV}                make a virtualenv in the base directory (see VENV)\n
  make init                   install python packages in requirements.txt\n
  make configure              configure aws user profile\n
  \n
  make list_stacks            run list_stacks helper script to list all Cloudformation stacks\n
  make create_stack           run create_stack script to setup workshop resources\n
endef
export PROJECT_HELP_MSG

help:
	echo -e $$PROJECT_HELP_MSG | less

VENV = venv
export VIRTUAL_ENV := $(abspath ${VENV})
export PATH := ${VIRTUAL_ENV}/bin:${PATH}

${VENV}: venv
	virtualenv $@

install: requirements.txt | ${VENV}
	source ./${VENV}/bin/activate
	pip install -r requirements.txt

configure:
	aws configure

list_stacks: scripts/list_stacks.py
	cd scripts && python list_stacks.py

create_stack: scripts/create_stack.py
	cd scripts && python create_stack.py

test_stack: scripts/test_stack.py
	py.test scripts/test_stack.py

clean:
	find . -type f -name "*.py[co]" -delete
	find . -type d -name "__pycache__" -delete

.PHONY: create_stack test_stack list_stacks install configure clean
