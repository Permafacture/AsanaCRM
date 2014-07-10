import re
from validators import sectionPattern,ValidationException
from secrets import ExpectedKeys, firstline_name,comma_exempt

def validate(key,values):
    '''
    based on the name of the key, validate the list of 
    values and return clean data'''
    #I just assume "values" is a list.  could easily coerce it 
    #  here if desired later)
    errorlog = []
    cleaned = []
    if key in ExpectedKeys.keys():
        validationFunction = ExpectedKeys[key]
        for value in values:
            try:
                cleaned.append(validationFunction(value))
            except ValidationException as ve:
                #if data doesn't validate than make note of it but move on! don't break over it.
                errorlog.append(ve.__str__())
    else:
        #was not expecting this key, so just clean it up as a string
        cleaned.extend([value.lstrip().rstrip() for value in values])

    return cleaned,errorlog


def to_dictionary(string):
    '''
    take marked up data from a multiline string into a list 
      of dictionaries like [{key:value},{key2:value}]


    The string looks like:
    
        firstline is title of object
        comments, comments everywhere
        key: data seperated by, commas 
        key: repeated keys appended to list of data

        +++++++
        
        Another section

        "Another section" (which gets it's name from the
        line above) will be its own entry, but has a
        connection to the parent also.  So, we can get
        all the sections that meet a certain criteria,
        and we can all the parents where they or their
        children meet that criteria.

        key: for,this,section


    New sections (list elements) are indicated by something 
    like '-----' or '++++++++'
         see sectionPattern
    '''
    string = string.encode('utf-8')  #always needed with web stuff.
    errorlog = []
    sections = re.split(sectionPattern,string,0,re.MULTILINE)
    result_list = []
    for section in sections:
        result_dict = {}
        data = section.lstrip().rstrip().split('\n')    #break into lines, ensure first line has data
        #The first line is important.  If its already got a keyword for it, great, other wise still save it!
        if ":" in data[0]:
          key,value = data[0].split(':')
          result_dict[key] = value
          result_dict[firstline_name] = value
        else:
          value = data[0]
          result_dict[firstline_name]=value
        #now process all the other lines
        for line in data[1:]:
          keyvalue = line.split(':')
          if len(keyvalue) == 1:
              pass
          elif len(keyvalue) == 2:
            #validate and clean data:
            #here we coerce key to be lowercase with no white space on sides
            key = str(keyvalue[0]).lstrip().rstrip().lower()
            #and data to be a list of strings
            if key in comma_exempt:
                #print type(keyvalue[1]),keyvalue[1]
                clean_data,errors = validate(key, [str(keyvalue[1])])
            else:
                clean_data,errors = validate(key, str(keyvalue[1]).split(','))

            #incase key is repeated, all data is in a list and repeating
            #the key appends it to the list.
            alist = result_dict.setdefault(key,[])    #create if necessary
            alist.extend(clean_data)    #alist is a pointer, so dictionary value is updated here
            errorlog.extend(errors)
            
          else:
            #This should be a ValidationException at some point:
            #if data doesn't validate than make note of it but move on! don't break over it.
            errorlog.append("Too many colons caused this: %s" % keyvalue)
        if errorlog:
          result_dict['errors'] = errorlog

        result_list.append(result_dict)
    return result_list
