FROM python:3.6
COPY LogOps/AuthenticationService ./
COPY requirements.txt ./
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8000
CMD [ "python", "SubscriptionServiceHTTP.py"]
