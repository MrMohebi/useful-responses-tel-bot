FROM python:3.9.17-alpine
COPY . .
RUN pip install -r requirements.txt

CMD ["python", "-u", "main.py"]