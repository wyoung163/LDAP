FROM python:3.8-slim

COPY . /app

RUN pip3 install flask 
RUN pip3 install ldap3

RUN --mount=type=secret,id=ldap ./
    cat /run/secrets/ldap > /app/keys.xml

WORKDIR /app

CMD ["python", "-m", "flask", "run", "--port=3000"]