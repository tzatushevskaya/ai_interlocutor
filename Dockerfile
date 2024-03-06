FROM mambaorg/micromamba:git-77b63de-jammy-cuda-12.2.2
USER root
WORKDIR /app
COPY ./environment.yml .
COPY ./requirements.txt .
RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/* && \
    micromamba shell init -p ~/micromamba -s bash && \
    source ~/.bashrc && \
    micromamba create -y -f /app/environment.yml && \
    micromamba clean -ay

RUN adduser -D appuser
USER appuser
COPY --chown=appuser:appuser . .
RUN mkdir /appfolder

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

CMD ["micromamba", "run", "-n", "myenv", "python", "main.py"]