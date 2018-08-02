test:
	pytest project/

e2e:
	@echo "Dropping fractal_e2e..."; \
	dropdb fractal_e2e --if-exists
	@echo "Creating fractal_e2e..."; \
	createdb fractal_e2e
	psql fractal_e2e < e2e-seed.dump
	DATABASE_URL="postgres://postgres:postgres@localhost:5432/fractal_e2e" python project/manage.py runserver

e2e-seed:
	pg_dump fractal_e2e > e2e-seed.dump

stagingdump:
	heroku pg:backups capture --app fractal-staging-app
	curl -o staging.dump `heroku pg:backups public-url`

loadstagingdump:
	dropdb fractalstagingdump --if-exists
	createdb fractalstagingdump
	pg_restore --verbose --clean --no-acl --no-owner -h localhost -U root -d fractalstagingdump staging.dump

proddump:
	heroku pg:backups capture --app fractal-production-app
	curl -o prod.dump `heroku pg:backups public-url --app fractal-production-app`

loadproddump:
	dropdb fractalproddump --if-exists
	createdb fractalproddump
	pg_restore --verbose --clean --no-acl --no-owner -h localhost -U root -d fractalproddump prod.dump
