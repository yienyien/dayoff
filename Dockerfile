FROM debian:bullseye-slim

RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    gnutls-bin\
    netcat \
    default-libmysqlclient-dev \
    # Clean
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir /backend
COPY requirements.txt /backend/requirements.txt

# To prevent from pillow bugs, need wheel package
RUN pip3 install --upgrade pip

RUN apt-get remove -y --purge python3-pip

RUN pip3 install -r /backend/requirements.txt

COPY . /backend/.
COPY docker-entrypoint.sh /
RUN chmod +x /docker-entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["/docker-entrypoint.sh"]
