FROM python:3.6
WORKDIR /code

# Install dependencies:
COPY requirements.txt /code/
RUN pip3.6 install -U pip setuptools \
    && pip3.6 install -r requirements.txt

COPY . /code/

EXPOSE 8000
CMD ["python", "easyorder/manage.py", "runserver", "0.0.0.0:8000"]
