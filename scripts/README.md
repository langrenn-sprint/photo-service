# scripts

A collection of simple scripts to load the database via the photo_service API.

```Shell
% poetry shell
% python load_competition_formats.py
```

You will need at least this in your .env to run it locally against the containers in this project:

```Shell
ADMIN_USERNAME=admin
ADMIN_PASSWORD=passw123
PHOTOS_HOST_SERVER=localhost
PHOTOS_HOST_PORT=8082
USERS_HOST_SERVER=localhost
USER_HOST_PORT=8080
```
