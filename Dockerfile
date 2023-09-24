FROM ubuntu
RUN apt update && \
apt install python3 python3-pip -y
COPY . /adt_send_hw/
WORKDIR /adt_send_hw
RUN pip install -r req.txt
ENTRYPOINT ["python3", "main.py"]