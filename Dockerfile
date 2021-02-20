FROM python:3

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN touch logfile.log
RUN ln -sf /proc/1/fd/1 logfile.log

CMD [ "python", "/usr/src/app/main.py" ]