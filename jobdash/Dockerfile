FROM ubuntu:18.04
RUN apt-get update && apt-get install python3-pip -y && pip3 install dash && pip3 install pandas
ADD mydashboard_4.1.py /home/mydashboard_4.1.py
WORKDIR /home/
CMD python3 mydashboard_4.1.py