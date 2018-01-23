FROM tiangolo/uwsgi-nginx-flask:python3.6

RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y \
	git \
	supervisor \
	vim && \
	pip3 install -U pip setuptools && \
    rm -rf /var/lib/apt/lists/*


COPY ./app /app
RUN pip3 install --no-cache-dir -r /app/requirements.txt

VOLUME /app
EXPOSE 80