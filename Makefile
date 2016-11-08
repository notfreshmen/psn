default: server

env:
	pyvenv venv

install:
	pip install --upgrade pip
	pip install -r requirements.txt

console:
	PYTHONSTARTUP=./console.py python

server:
	python ./server.py

test:
	AMABLE_ENV=test mamba --enable-coverage --format=documentation

lint:
	pycodestyle .

js_lint:
	standard ./amable/assets/jsc/**/*.js

coverage:
	coverage report

dbsetup:
	createuser -U postgres -h localhost -p 5432 -d -w amable
	sudo -u postgres psql -U postgres -c "alter user amable with password 'domislove';"

db_user_setup:
	createuser -U postgres -h localhost -p 5432 -d -w amable
	sudo -u postgres psql -U postgres -c "alter user amable with password 'domislove';"

psql:
	psql -U amable -d amable_development


dbsync:
	export PGPASSWORD='domislove'

	# amable_development ~~ Drop->Create->Version Control->InitDB->[INIT DATA]
	dropdb -U amable amable_development --if-exists
	createdb -U amable -O amable -h localhost -p 5432 amable_development
	python db/manage.py version_control
	python db/manage.py upgrade

	# amable_test ~~ Drop->Create->Version Control->InitDB->[INIT DATA]
	dropdb -U amable amable_test --if-exists
	createdb -U amable -O amable -h localhost -p 5432 amable_test
	AMABLE_ENV=test python db/manage.py version_control
	AMABLE_ENV=test python db/manage.py upgrade

reinit:
	psql -U amable -d amable_development -c 'delete from comments; delete from posts; delete from communities; delete from users;'
	python data_init.py

erd:
	eralchemy -i postgres://amable:domislove@localhost:5432/amable_development -o docs/erd.pdf
