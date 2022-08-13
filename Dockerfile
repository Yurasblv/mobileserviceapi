FROM python:3.10
WORKDIR /lampatest
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
RUN pip install --upgrade pip
COPY requirements.txt .
COPY ./start.sh /bin/start.sh
RUN chmod +x /bin/start.sh
RUN pip install -r requirements.txt
COPY . /lampatest
EXPOSE 8000
CMD /bin/sh -c '/bin/start.sh'