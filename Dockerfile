FROM python:3.8.1-alpine

WORKDIR /usr/src/app

COPY . .

CMD ["python", "-m", "test_delimited_writer"]