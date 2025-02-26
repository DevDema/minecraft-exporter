FROM arm64v8/python:3.10.16-alpine

COPY requirements.txt minecraft_exporter.py /
RUN pip install --no-cache-dir -r requirements.txt

COPY tests /tests

RUN python -m unittest discover -s tests

EXPOSE 8000

ENTRYPOINT ["python","-u","minecraft_exporter.py"]
