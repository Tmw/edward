FROM tensorflow/tensorflow:latest-py3

RUN mkdir /edward
RUN mkdir /edward/tfmodel
WORKDIR /edward

COPY requirements.txt ./requirements.txt
COPY *.py ./
COPY tfmodel/* ./tfmodel/

RUN pip install -r ./requirements.txt

CMD ["python", "main.py"]


