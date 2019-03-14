FROM openlabs/docker-wkhtmltopdf-aas
RUN echo "deb http://archive.ubuntu.com/ubuntu/ trusty multiverse" > /etc/apt/sources.list.d/multiverse.list
RUN apt-get update && apt-get install -y ttf-mscorefonts-installer

ADD app.py /app.py