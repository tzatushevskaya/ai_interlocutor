ARG PLATFORM=linux/amd64
ARG BASE_IMAGE="mambaorg/micromamba:1.5.1"

FROM --platform=$PLATFORM ${BASE_IMAGE}

# Set the working directory in the container
WORKDIR /app

# Install any needed packages specified in requirements.txt
COPY . ./
USER root
RUN apt-get update && apt-get install -y ffmpeg libavcodec-extra && apt-get clean
RUN export CONDA_PREFIX=/root/micromamba && micromamba shell init -p ~/micromamba -s bash && source ~/.bashrc \
    && micromamba activate && micromamba install python=3.12 -y -c conda-forge \
    && pip install -e . \
    && micromamba clean -ay \
    ffdl install -y

ENTRYPOINT source ~/.bashrc && micromamba activate && interlocutor_cli