AsanaCRM
========

Python scripts for using a single asana project as a CRM by 
recognizing markdown in the task descriptions and making 
queriable objects that can be output as speadsheets.

details
=======
One works with a QueryList object, which is a list of
dictionaries (each representing an Asana task) 
with keys here called field names. A QueryList can 
filter itself based on user defined field names, as 
well as meta data related to Asana tasks

The markup in an Asana task that is recognized as
a field name is "my field name: it's value".  To the 
left of the colon defines the field name, and to the 
right the value of that field.

Additionally, the first line of a task has special 
importance.  It becomes the value of a field name 
defined in the set-up file "secrets.py".  "name"
is a very reasonable value for this in a CRM.

There are also meta data field names which all
begin with a "."

As of the time of this writing, the meta field names
are:

.id   #the Asana id of the task
.link #html used to link to the project
.created #datetime object of the creation date
.name  #the Asana name for the task
.url   #the url of the task

finally, a string of at least 5 special characters 
(/*-+=#!%\^.) defines a new section within a task 
(ie, children of the parents)

A marked up task might look like:

        Uncle Bob
        comments, comments everywhere
        phone: 123-456-1234x222, (234) 564.1526
        The validators are robust! Also each field
        can have multiple items, seperated by commas
        or by additional entries, like...
        phone: 254.123.2345
        Uncle Bob now has 3 phone numbers

        +++++++
        Cousin Louie

        "Cousin Louie" (which gets it's name from the
        line above) will be its own entry, but has a
        connection to the parent also.  So, we can get
        all the sections that meet a certain criteria,
        and we can all the parents where they or their
        children meet that criteria.

        email: cousin@thefamily.com


install
=======

    pip install -r requirements.txt


setup
=====

Edit secrets.py.example with your asana information and 
and save it as secrets.py

run asanaCRM.py 

This will (slowly) build a local file that is the source
of data for queries.  This file will need to be rebuilt
if you have changed any CRM entries in asana.

Check output/errors.html to see any individuals with fields
that failed validation, and a display of all the field names
found and their frequency.  The latter is helpful for 
recognizing that both "email" and "e-mail" are being used,
for example.

open up a python shell (preferably Ipython), build querysets
  and export as files. 

queries are strings in the format of "fieldname_operatorname",
where fieldname is some

see common_queries.py for examples of how to make queries



