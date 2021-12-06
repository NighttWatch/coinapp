# Base Image - First Stage
FROM python:3.9 AS firststage

#Run requrements to user field (/root/.local)
RUN pip install --user -r requirements.txt

#Second Stage
FROM python:3.9-slim

#Work Path
WORKDIR ./

#COPY to first stage requirements folder to second stage
COPY --from=firststage /root/.local /root/.local

#local to copy folder to container
COPY . .
#run
CMD [ "python","-u" ,"./distributor.py" ]

#Update path information
ENV PATH=/root/.local:$PATH