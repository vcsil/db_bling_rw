# using ubuntu LTS version
FROM ubuntu:22.04 AS builder-image

# avoid stuck build due to user prompt
ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get update && \
	apt-get install --no-install-recommends -y python3.11 python3.11-dev python3.11-venv python3-pip python3-wheel build-essential && \
	apt-get clean && \
	rm -rf /var/lib/apt/lists/*

# create and activate virtual environment
# using final folder name to avoid path issues with packages
RUN python3.11 -m venv /home/myuser/venv
ENV PATH="/home/myuser/venv/bin:$PATH"

# install requirements
COPY ./db_criacao/configura_banco_de_dados_rapido/preencher/requirements.txt .
RUN pip3 install --upgrade pip
RUN pip3 install --no-cache-dir wheel
RUN pip3 install --no-cache-dir -r requirements.txt

# Constroi imagem ubuntu
FROM ubuntu:22.04 AS runner-image

RUN apt-get update && \
	apt-get install --no-install-recommends -y python3.11 python3-venv wget gnupg2 apt-transport-https ca-certificates software-properties-common libnss3 curl unzip vim && \
	apt-get clean && \
	rm -rf /var/lib/apt/lists/*

# Add the Google Chrome repository
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list
# Install Google Chrome
RUN apt-get update && apt-get install -y google-chrome-stable \
    && rm -rf /var/lib/apt/lists/*
# Add the Chrome as a path variable
ENV CHROME_BIN=/usr/bin/google-chrome
ENV DISPLAY=:99

# Set TimeZone
ENV TZ=America/Sao_Paulo
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

RUN useradd --create-home myuser
COPY --from=builder-image /home/myuser/venv /home/myuser/venv

USER myuser
RUN mkdir /home/myuser/code
WORKDIR /home/myuser/code
COPY . .

# EXPOSE 5000

# make sure all messages always reach console
ENV PYTHONUNBUFFERED=1

# activate virtual environment
ENV VIRTUAL_ENV=/home/myuser/venv
ENV PATH="/home/myuser/venv/bin:$PATH"


CMD ["python", "/home/myuser/code/db_criacao/configura_banco_de_dados_rapido/preencher/preencher_banco_de_dados.py"]
# CMD ["pwd"]
