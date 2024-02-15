ARG PLATFORM=linux/amd64
ARG BASE_IMAGE="mambaorg/micromamba:1.5.1"

FROM --platform=$PLATFORM ${BASE_IMAGE} as development

USER root
WORKDIR /app
COPY . .
RUN export CONDA_PREFIX=/root/micromamba && micromamba shell init -p ~/micromamba -s bash && source ~/.bashrc \
    && micromamba activate && micromamba install python=3.11 -y -c conda-forge \
    && pip install -e . \
    && micromamba clean -ay

ENTRYPOINT source ~/.bashrc && micromamba activate && interlocutor_cli