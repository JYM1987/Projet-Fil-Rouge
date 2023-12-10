FROM ubuntu:18.04
RUN apt-get update && apt-get install python3-pip -y && pip3 install requests && pip3 install pymongo
ADD * /home/* 
WORKDIR /home/
CMD python3 PE_extraction.py; python3 PE_transform.py; python3 PE_ml.py; python3 PE_load.py