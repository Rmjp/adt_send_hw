FROM ubuntu
RUN apt update && \
apt install python3 python3-pip iproute2 iputils-ping -y
WORKDIR /adt_send_hw
COPY . /adt_send_hw/
RUN pip install -r req.txt
EXPOSE 3001
CMD ["python3", "main.py"]
