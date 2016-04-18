import re
import datetime
strptime = datetime.datetime.strptime



class ValidationException(Exception):
    def __init__(self, value):
        self.parameter = value
    def __str__(self):
        return repr(self.parameter)




phonePattern = re.compile(r'''
                # don't match beginning of string, number can start anywhere
    (\d{3})     # area code is 3 digits (e.g. '800')
    \D*         # optional separator is any number of non-digits
    (\d{3})     # trunk is 3 digits (e.g. '555')
    \D*         # optional separator
    (\d{4})     # rest of number is 4 digits (e.g. '1212')
    \D*         # optional separator
    (\d*)       # extension is optional and can be any number of digits
    $           # end of string
    ''', re.VERBOSE)

#a date may be dd/mm/yyyy, d/m/yyyy, mm/yyyy, m,yyyy, or yyyy
datePattern = re.compile(r'''
                # don't match beginning of string, number can start anywhere
    (\d{1,2})*  # optional 1 or two digit day
    \D*         # optional separator is any number of non-digits
    (\d{1,2})*  # optional one or two digit month
    \D*         # optional separator
    (\d{4})    # not optional four digit year
    $           # end of string
    ''', re.VERBOSE)

#at least 5 punctiation marks starting a line
sectionPattern = r'^[/*-+=#!%\^.]{5,}'


def validatePhone(string):
    string=string.lstrip().rstrip()
    processed = phonePattern.search(string)
    if not processed:
        raise ValidationException("'%s' doesn't contain a valid phone number" %string)
    else:
        groups = processed.groups()
        if groups[3]:
            return "(%s) %s-%s ext: %s" % groups
        else:
            return "(%s) %s-%s%s" % groups #fourth group is empty, btw

def validateEmail(string):
    string = string.lstrip().rstrip()
    if not re.match("[^@]+@[^@]+\.[^@]+", string):
    #print "did this"
        raise ValidationException("'%s' is not a valid email address" % string)
    else:
        return string

def validateBool(string):
    string = string.lstrip().rstrip().lower()
    if string in {'yes','no'}:
        return string == 'yes' #return True or False
    else:
        raise ValidationException("'%s' is not a bool (yes or no)" % string)

def validateDate(string):
    string =string.lstrip().rstrip()
    processed = datePattern.search(string)
    if not processed:
        raise ValidationException("'%s' doesn't look like a date" % string)
    else:
        groups = processed.groups()
        if not groups[1]:
            if not groups[0]:
                #recieved (None, None, YYYY)
                 format = "None None %Y"
            else:
                #recieved (MM,None,YYYY)
                format = "%m None %Y"
        else:
            #recieved (mm,dd,yyyy)
            format = "%m %d %Y"
    data = "%s %s %s" % groups
    #print data  
    try:  
        date = strptime(data, format)
    except ValueError:
        raise ValidationException('[%s] does not fit date format [%s]' %(data,format))
    return date



