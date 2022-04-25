FROM python:3
WORKDIR /home_app

ENV FLASK_APP BackendAPI.py
ENV FLASK_RUN_HOST 0.0.0.0
ENV FLASK_RUN_PORT 5000
ENV FLASK_ENV development

COPY ./home_app /home_app
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

CMD [ "python3", "-m" , "flask", "run"]