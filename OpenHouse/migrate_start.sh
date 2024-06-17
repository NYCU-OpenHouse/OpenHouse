git submodule init
git submodule update --recursive
python3 ./manage.py makemigrations staff
python3 ./manage.py migrate staff
python3 ./manage.py migrate
python3 ./manage.py migrate --database=oh_2023
python3 ./manage.py makemigrations general
python3 ./manage.py migrate general
python3 ./manage.py makemigrations company_visit
python3 ./manage.py migrate company_visit
python3 ./manage.py makemigrations company
python3 ./manage.py migrate company
python3 ./manage.py makemigrations careermentor
python3 ./manage.py migrate careermentor
python3 ./manage.py makemigrations recruit
python3 ./manage.py migrate recruit --database=oh_2023
python3 ./manage.py makemigrations rdss
python3 ./manage.py migrate rdss --database=oh_2023
python3 ./manage.py makemigrations vote
python3 ./manage.py migrate vote
python3 ./manage.py makemigrations monograph
python3 ./manage.py migrate monograph
python3 ./manage.py migrate
python3 ./manage.py migrate --database=oh_2023
python ./manage.py runserver 0.0.0.0:8000