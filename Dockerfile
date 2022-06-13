FROM python:3.10

WORKDIR /imse_m2_team27
ADD . /imse_m2_team27
RUN pip install -r requirements.txt
ENTRYPOINT ["python"]
CMD ["run.py"]