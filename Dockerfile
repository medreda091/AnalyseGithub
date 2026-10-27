FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt requirements-dev.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY analyse_github ./analyse_github
COPY exemples ./exemples
ENTRYPOINT ["python", "-m", "analyse_github.cli"]
CMD ["--exemple"]
