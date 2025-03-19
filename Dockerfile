FROM ubuntu:22.04

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    python3-venv \
    python3-pip \
    make \
    wget \
    ffmpeg \
    libsm6 \
    libxext6 \
    libjpeg-dev \
    libpng-dev \
    libturbojpeg \
    curl \
    pciutils

WORKDIR /pdf_parcer

COPY requirements.txt requirements.txt
COPY ollama_pull_models.sh ollama_pull_models.sh
RUN chmod +x ollama_pull_models.sh
COPY Makefile Makefile
RUN make install
RUN make download_models
COPY . .

EXPOSE 5045

CMD make run_app_docker
