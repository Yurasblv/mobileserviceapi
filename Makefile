environ:
	sudo pip install --user pipenv
	sudo pipenv shell
start:
	sudo docker-compose up
stop:
	sudo docker-compose down
clean:
	sudo docker system prune -af