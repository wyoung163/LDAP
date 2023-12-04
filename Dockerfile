FROM python:3.8

COPY . /app

RUN pip3 install flask
RUN pip3 install ldap3

WORKDIR /app

RUN --mount=type=secret,id=ldap \
        cat /run/secrets/ldap > /app/keys.xml

CMD ["python", "-m", "flask", "run", "--host=0.0.0.0", "--port=3000"]
