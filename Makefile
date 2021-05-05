default:
	@echo
	@echo "Examples:"
	@echo "	   make run:    #To run the go into virtual env, set up env vars and run locally"
	@echo

	
run:
	source venv/bin/activate && source .env && python app.py

db:
	 rm -rf migrations
	python manage.py db init
	python manage.py db migrate
	python manage.py db upgrade


