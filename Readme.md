# ACUITEE (Annotation and Curation User Interface for Terms Extraction Engines)
ACUITEE represents a web application with three main functionalities: visualization, editing and manual curation of the annotation results proposed by automatic parsers.

# Instructions

1.	Clone the source codes and put them on some directory on your local machine.
2.	Create a virtual environment (python 3.9) with ``apt install python3.9-venv`` then ``python3 -m venv venv``
3.	Activate you virtual environment with ``venv\scripts\activate`` or(``source venv/bin/activate``)
4.	Install the requirements: ``pip install -r requirements.txt``
5.	To run the application, you have two options:
    - Development: from the terminal, type ``flask run``. This will run the application with the flask development server and with ``FLASK_ENV=development``. See the file “.flaskenv”.
    - Production: from the terminal, type ``python main.py``. This will run the application with gevent server.

# Human Phenotype Ontology (HPO)
This web application, ACUITEE, uses the Human Phenotype Ontology (08/02/2021). Find out more at [http://www.human-phenotype-ontology.org](http://www.human-phenotype-ontology.org)

<img src="https://github.com/b-com/ACUITEE/blob/main/HPO_logo.png?raw=true" style="background-color:blue ;" alt="HPO" width="50"/>
