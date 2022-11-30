.PHYONY = help run setup

port := 8000

help:
	@echo "---------------HELP-----------------"
	@echo "To setup the project type make setup"
	@echo "To clean the project type make clean"
	@echo "To run the project type make run"
	@echo "------------------------------------"

setup:
	@echo "Setting up project..."
	python -m pip install --upgrade pip
	python -m pip install -r requirements.txt
	python -m pip install -e .

run:
	@echo "Running project on port $(port)"
	uvicorn main:app --reload --port $(port)

clean:
	rm -rf __pycache__

