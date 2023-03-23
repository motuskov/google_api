# Create the environment for Django project
FROM python:alpine
WORKDIR /google_api
COPY google_api .
RUN pip install -r requirements.txt
EXPOSE 8000
