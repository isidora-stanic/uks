# lightweight linux container
FROM alpine

# setup working directory
RUN mkdir /code
WORKDIR /code
ADD . /code

# setup python tools
RUN apk add --update \
         python3 \
         python3-dev \
         py-pip \
         build-base
RUN pip install --upgrade pip
# installing requirements
RUN pip install -r requirements.txt
# change dir
WORKDIR mini_githubcic
# setup Django project and db
RUN python3 manage.py makemigrations
RUN python3 manage.py migrate
RUN python3 manage.py fill_database
# port that server uses
EXPOSE 8000
# run Django develop server
CMD ["python3", "manage.py", "runserver", "0.0.0.0:8000"]
