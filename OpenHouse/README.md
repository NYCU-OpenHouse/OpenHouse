
## Running on your host

### Dependency

#### pip

+ Django >= 1.9
+ django-ckeditor
+ Pillow
+ mysqlclient
+ Xlsxwriter

#### other
+ CKEditor

### Settings.py

Make sure two things:

1. There is a file named `settings.py` in `OpenHouse` folder.
2. The database username and password settings are correct. 
<br/>(There is a sample setting.py in `dev_tools/settings.py.sample`)

### Database Migration

+ `python manage.py makemigrations`
+ `python manage.py migrate`
+ `python manage.py migrate --database=oh_2017`

### Run the development server

`python manage.py runserver [IP]:[PORT]`

