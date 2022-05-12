# ACUITEE (Annotation and Curation User Interface for Terms Extraction Engines)
ACUITEE represents a web application with three main functionalities: visualization, editing and manual curation of the annotation results proposed by automatic parsers.


##

# Author & Contributors
#### Author: 
Majd SALEH, PhD, Research & Development Engineer, Artificial Intelligence Laboratory, IRT b<>com, France
#### Contributors: 
* Majd SALEH, Stéphane PAQUELET, Cyndie MARTIN, IRT b<>com, France
* Marie DE TAYRAC, Paul ROLLIER, Wilfried CARRE, Chrystele DUBOURG and Sylvie ODENT, CHU de Rennes, France
* Guillaume COLLET and Olivier DAMERON, Univ. Rennes 1, France
* Thomas LABBE and Jean-Michel SANNER, Orange, France

##

# Instructions

1.	Clone the source codes to your local machine.
2.	Create a virtual environment (python 3.9) with ``apt install python3.9-venv`` then ``python3 -m venv venv``
3.	Activate you virtual environment with ``venv\scripts\activate`` or(``source venv/bin/activate``)
4.	Install the requirements: ``pip install -r requirements.txt``
5.	To run the application, you have two options:
    - Development: from the terminal, type ``flask run``. This will run the application with the flask development server and with ``FLASK_ENV=development``. See the file “.flaskenv”.
    - Production: from the terminal, type ``python main.py``. This will run the application with gevent server.
##
For using ACUITEE as a Docker container, execute the following steps (instead of steps ``2 to 5``above):
1. Build the Docker image: use your CLI and navigate to the directory of ACUITEE. For example: ``C:\Users\msaleh\Development\ACUITEE>``
2. Execute the following command: ``docker build --tag acuitee .``
3. Run the docker image by executing the following command: ``docker run -d --publish 5000:5000  --name "acuitee" acuitee``
where ``-d`` is used to make the container (i.e. the running image) working in a detached mode i.e. as a background service in the OS.
``--publish`` is used to make the port ``5000`` on the container visible from the port ``5000`` of the host (without this, we will not be able to interact with the container). 
4. Use your favorite browser, go to the following URL to access the web application ACUITEE:
``http://localhost:5000/``
5. To stop the docker container, use the command ``docker stop acuitee``
6. To start the docker container again, use: ``docker start acuitee``

# Human Phenotype Ontology (HPO)

This web application, ACUITEE, uses the Human Phenotype Ontology (08/02/2021). Find out more at [http://www.human-phenotype-ontology.org](http://www.human-phenotype-ontology.org)

<img src="https://github.com/b-com/ACUITEE/blob/main/HPO_logo.png?raw=true" style="background-color:blue ;" alt="HPO" width="50"/>
