FROM raspbian/jessie

RUN apt-get update 

RUN apt-get install -y apache2 && apt-get clean

RUN apt-get install -y python3 python3-pip python3-virtualenv python3-dev && apt-get clean

ADD Hornet2 /app/

WORKDIR /app

RUN pip3 install -r requirements.txt

CMD python3 wsgi.py

EXPOSE 5000
