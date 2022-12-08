FROM python:3.6

RUN python3 -m venv /opt/venv

WORKDIR /code

COPY requirements.txt ./
RUN /opt/venv/bin/pip install -r requirements.txt

ADD . .

EXPOSE 8000
# CMD ["python", "easyorder/manage.py", "runserver", "0.0.0.0:8000"]
RUN python -v