# Base Image - First Stage
FROM python:3.9

WORKDIR /sandbox

COPY requirements.txt requirements.txt
#Run requrements to user field (/root/.local)
RUN pip3 install -r requirements.txt

#local to copy folder to container
COPY . .
#run
CMD [ "python","-u" ,"./distributor.py" ]