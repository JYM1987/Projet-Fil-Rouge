FROM ubuntu:18.04
RUN apt-get update && apt-get install python3-pip -y && pip3 install requests && pip3 install pymongo && pip3 install pandas && pip3 install scikit-learn
COPY * /home/ 
WORKDIR /home/
CMD python3 PE_load.py
