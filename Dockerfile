FROM python:3.6
COPY LogOps/AuthenticationService/SubscriptionServiceHTTP.py ./
COPY requirements.txt ./
RUN pip3 install -r requirements.txt
COPY . .
EXPOSE 8000
CMD [ "python3", "-u", "SubscriptionServiceHTTP.py"]