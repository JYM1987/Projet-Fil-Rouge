FROM ubuntu:18.04
RUN apt-get update && apt-get install python3-pip -y && pip3 install dash && pip3 install pandas && pip3 install dash_bootstrap_components && pip3 install pymongo
ADD mydashboard_4.2.py /home/
WORKDIR /home/
CMD python3 mydashboard_4.2.py
