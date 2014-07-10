AsanaCRM
========

Python scripts for using a single asana project as a CRM by recognizing markdown in the task descriptions and making a queriable objects that can be output as speadsheets

install
=======

    pip install -r requirements.txt

setup
=====

edit secrets.py.example with your asana information and 
 and save it as secrets.py

run asanaCRN.py 

This will (slowly) build a local file that is the source
 of data for queries.  This file will need to be rebuilt
 if you have changed any CRM entries in asana.

open up a python shell (preferably Ipython), build querysets
  and export as files.

see common_queries.py for examples of how to make queries



