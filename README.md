django-channels-chat
===

Group chat using django channels


### Installation
```
$ pip install -U channels
```

>Note: Recommended to install this in a virtualenv


### flow
```
    login ----> add chat room ---> start chatting
```


### Run the following using:
```
$ python manage.py runserver
```

>Note: redis is used as channel backend and mongoDB is used for message persistence.
       Make sure they are installed and running in background



