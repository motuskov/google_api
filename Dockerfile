FROM python:alpine AS base
WORKDIR /google_api
COPY google_api .
RUN pip install -r requirements.txt
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
EXPOSE 8000
