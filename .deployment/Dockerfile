FROM python:3.11
LABEL Description="django-formset testapp" Maintainer="Jacob Rief"
RUN mkdir /web
WORKDIR /web

# install packages outside of PyPI
RUN apt-get upgrade -y
RUN apt-get install -y curl make
RUN curl -sL https://deb.nodesource.com/setup_16.x | bash -
RUN apt-get install -y nodejs npm
RUN pip install --upgrade pip

# install Node specific requirements
COPY package.json /web/package.json
COPY package-lock.json /web/package-lock.json
RUN ls -lR /usr
RUN npm ci

# install Python specific requirements
RUN pip install django psycopg2-binary Pillow uWSGI docutils Sphinx sphinx-toolbox
RUN pip install https://github.com/pradyunsg/furo/archive/refs/heads/main.zip
RUN pip install https://github.com/jrief/django-sphinx-view/archive/refs/heads/main.zip

# copy project relevant files into container
ADD assets /web/assets
ADD client /web/client
ADD docs /web/docs
ADD formset /web/formset
ADD testapp /web/testapp
COPY .deployment/uwsgi.ini /etc/uwsgi.ini
COPY .deployment/entrypoint.sh /web/entrypoint.sh

# compile assets
RUN npm run tag-attributes
RUN npm run compilescss
RUN npm run tailwindcss
RUN npm run esbuild

# create documentation
RUN npm run docscss
RUN make --directory=docs json

# handle static and media files
ENV DJANGO_STATIC_ROOT=/web/staticfiles
ENV DJANGO_WORKDIR=/web/workdir
ENV DJANGO_MEDIA_ROOT=/web/workdir/media
ENV DJANGO_SECRET_KEY=dummy_secret_key
ENV PYTHONPATH=/web
RUN mkdir -p $DJANGO_STATIC_ROOT
RUN ./testapp/manage.py collectstatic --noinput

# handle permissions
RUN useradd -M -d /web -s /bin/bash django
RUN chown -R django.django $DJANGO_STATIC_ROOT

EXPOSE 8080

ENTRYPOINT ["/web/entrypoint.sh"]
CMD ["uwsgi"]
