# the web

The Web component prototype for Superdesk. Renders content stored in MongoDB.

### install using python3

    pip install -r requirements3.txt

### run dev server

    python manage.py runserver [host:port]

### run wsgi server e.g. gunicorn

    gunicorn wsgi

### static files - will collect from apps into root static folder

    python manage.py collectstatic

now you can set your web server to serve ```/static/``` url from ```static/``` folder
