import secrets
from pickle import load
import datetime
from operator import itemgetter
import csv 
from collections import defaultdict
strptime = datetime.datetime.strptime
#can I use set(QL.copy().query('one_query').extend(QL.copy().query('nother_query')) to OR?

class QueryList(list):
    '''Assumes list is of the format produced by pickle_asana_project'''

    queries = []    #a list of queries performed to get to current point

    def __init__(self,*args,**kwargs):
	list.__init__(self,*args,**kwargs)
	self.reset() 

    def reset(self):
	'''refesh values from pickled list in pickle file'''
	self.__delslice__(0,len(self))
	with open(secrets.pickle_file,'rb') as fp:
	    self.extend(load(fp))
	self.queries = []
	print "QueryList contains %s entries" % len(self)

    def query(self,string):
	'''querylist.query('email_exists, dob_before_2011')
	modifies self to contain only the results.'''
	args = string.split(',')
	for arg in args:
	    #pieces loos like [function,argument1,other,arguments]
	    pieces = arg.lstrip().rstrip().lower().split('_')
	    try:
		methodToCall = getattr(self, "_"+pieces[1])
	    except AttributeError:
		print '\nError: %s is not a known query function' % pieces[1]
		
	    else:
		self.queries.append(arg)	#this query was performed
		tmp = []
		for item in self:
		    #Check pass or fail of each item in self according to this query function 
		    if methodToCall(pieces,item):
			    tmp.append(item)
		#Update the result of this QueryList
		#delete all old items and replace with new
		self.__delslice__(0,len(self))
		self.extend(tmp)
		print "Query resulted in %s entries remaining" % len(self)


    """
    def annotate(f, name='annotation',*args,**kwargs):
	'''call f(item, *args,**kwargs) on every item in the QueryList.
	    f must know the structure of item inorder to operate on it, and should
	    return None if it fails for any reason.
	    The result is stored in the dictionary "item" under the name given as a keyword'''

	for item in self:
	    result = f(item,*args,**kwargs)
	    item[name] = result
    """

    def output_as_html(self,fieldnames,query=True, outfile=secrets.output_html):
	'''Make an html table with the fieldnames provided
		Usage:
		output_as_html(".link,email, dob, etc","output.html"'''
	fields = [x.lstrip().rstrip().lower() for x in fieldnames.split(',')]
	with open(outfile,'wb') as fp:
	    if query:
		queries = 'The following queries returned these results: '
		queries += ', '.join(self.queries).replace('_',' ')
	    else:
		queries = ''
	    fp.write('<html><body><p>%s</p><table>' % queries )
	    line = '<tr>'
	    for field in fields:
		line += '<td>%s</td>' % field
	    line +='</tr>'
	    fp.write(line)
	    print fields[0]
	    for dictionary in self:
		#for dictionary in self:
		line = '<tr>'
		for kw in fields:
		    try:
			line += '<td>%s</td>' % formatter(dictionary[kw])
		    except KeyError:
			print kw+' not found'
			line += '<td>[n/a]</td>'
		line+='</tr>'
		fp.write(line)

	    fp.write('</table></body></html>')
	print "output saved as %s" % outfile

    def output_as_csv(self,fieldnames,query=True, outfile=secrets.output_csv):
        '''Make an html table with the fieldnames provided
                Usage:
                output_as_html(".link,email, dob, etc","output.html"'''
        fields = [x.lstrip().rstrip().lower() for x in fieldnames.split(',')]
        with open(outfile,'wb') as fp:
	    writer = csv.writer(fp,delimiter='\t', quotechar='"')
            if query:
                queries = 'The following queries returned these results: '
                queries += ', '.join(self.queries).replace('_',' ')
                writer.writerow([queries])
                print "i did this"
            writer.writerow(fields)
            print "and this"
            for dictionary in self:
		line = []
                for kw in fields:
                    try:
                        line.append(formatter(dictionary[kw]))
                    except KeyError:
                        line.append('[n/a]')
                writer.writerow(line)

        print "output saved as %s" % outfile

    def _exists(self,pieces,item):
	''' search the data for the existance of the keyword (the 'email' in 'email_exists').
	{keyword: []} is a false, since there is no data'''
	kw = pieces[0]	#keyword is always first argument
	#mmm, changed my mind.  If keyword is initialized but empty, it still exists
	#try:
	#    return bool(item[kw])
	#except KeyError:
	#    return False
	return kw in item.keys()
	

    def _doesntexist(self,pieces,item):
	''' inverse of exists'''
	return not self._exists(pieces,item)
 

    def _before(self,pieces,item):
	'''as in dob_before_2012.  only years are currently supported, and dates found under "data" '''
	if self._exists(pieces,item):
	    kw = str(pieces[0])	    #keyword
	    year = str(pieces[2])
	    target = strptime(year,"%Y")
	    tocheck = item[kw]
	    return tocheck <= target
	else:
	    #keyword doesn;t even exist!
	    return False


    def _after(self,pieces,item):
	'''as in dob_before_2012.  only years are currently supported, and dates found under "data" '''
	if self._exists(pieces,item):
	    kw = str(pieces[0])
	    year = str(pieces[2])
	    target = strptime(year,"%Y")
	    tocheck = item[kw]
	    return tocheck >= target
	else:
	    #keyword doesn;t even exist!
	    return False

    def _contains(self,pieces,item):
	'''usually: ".notes_contains_this phrase"'''
	if self._exists(pieces,item):
	    kw=pieces[0]    #keyword
	    phrase = pieces[2]
	    if phrase in item[kw]:
		return True
	return False

    def _is(self,pieces,item):
	'''.id_is_14'''
	if self._exists(pieces,item):
	    kw=pieces[0]    #keyword
	    phrase = pieces[2]
	    if str(phrase).strip() == str(item[kw]).strip():
		return True
	return False


    def _enrolled(self,pieces,item):
	'''If called as not_enrolled, returns all those not enrolled.  Anything else return all enrolled. 
	Like, is_enrolled, booger_enrolled, etc.'''
	result = False	
	if self._exists(['enrolled'],item):
	    #if they have ever been enrolled
	    if self._exists(['withdrew'],item):
		#they have been enrolled before, and have withdrawn before.  Where are they currently?
		if len(item['enrolled']) > len(item['withdrew']):
		    #they have enrolled more times than they've withdrawn, so they are currently enrolled
		    result = True
		else:
		    result = False
	    else:
		#they have enrolled and never withdrawn, so they are enrolled
		result = True
	else:
	    #they have never enrolled
	    result = False  
	if pieces[0] == 'not':
	    result = not result
	return result

    def stats(self):
	''' return a dictionary where each key is a key found in the query results
	and the value is the number fo times it occurs'''
	result = {} 
	for item in self:
	    for key in item.keys():
	        result.setdefault(key,0)
		result[key] += 1
	for key,value in sorted(result.items()):
	    print '%s: %s' % (key,value)

    def convert_to_parents(self):
	'''Return a QueryList of the parents of the results in the current list'''
	QL = QueryList()
	QL.reset()
	QL.query('.parent_exists')
	ids = set([item['.id'] for item in self])
	tmp = []
	for i,parent in enumerate(QL):
	    if parent['.id'] in ids:
		tmp.append(parent)
	QL.__delslice__(0,len(QL))
	QL.extend(tmp)
	QL.queries = self.queries[:]	#a copy so it doesn't get changed later
	QL.queries.append("convert to parent's entries")
	return QL

    def sort(self,key):
        tmp = sorted(self, key=lambda k: k.get(key,'zzzzzz'))
        self.__delslice__(0,len(self))
        self.extend(tmp)

def formatter(unknown_type):
    '''take an unnamed type and return its prefered representation'''
    result = unknown_type 
    #print type(result),result
    if type(result) == list:
	#clever recursion
	result = ', '.join([formatter(x) for x in result])
    elif type(result) == datetime.datetime:
	result = result.strftime('%m/%Y')
    elif type(result) == datetime.timedelta:
	#print "called"
	result = result.days
    elif type(result) == float:
	result = '%.1f' % result
    return str(result)

def sorter(dic):
    '''prototype sorter function.  Sorts on the 'name' keyword, even if it doesn't exist
    those without names go up top to be visible'''
    #this could take an argument if it was defined as a function that took that one argument and returned
    # a function that took a dict as its argument.
    try:
	a = dic[secrets.firstline_name]
    except KeyError:
	#There would be a key error if the asana item had no notes, and so no first line
	#this is obviously an error and should be made visible at the top of the list
	return 0
    else:
	#my best shot at getting the last name.
	return a.split(' ')[-1]

def time_enrolled(ql):
    '''takes a QueryList and for anything with an 'enrolled' keyword, adds another key 
    with the total time spent enrolled in school as the value.  Uses a 'withdrew' keyword
    in the calculation if it exists, where the first enrollment is ended by the first 
    withdrawl'''
    #please note that key names must have no white space on the sides and be all lowercase
    #spaces in the middle are okay.  dont use '_' because of query syntax collisons
    aggregate_fieldname = 'days enrolled'
    cntr = 0
    for item in ql:
	e = item.get('enrolled',[])
	w =item.get('withdrew',[])
	lene = len(e)
	lenw = len(w)
	#print lene
	if lene == 0:
	    #never enrolled.  Why did you ask?
	    #well, you can now filter on the existance of aggregate_field_name if you want to.
	    pass
	elif -1 >= lene-lenw >= 2:
	    raise ValueError('Corrupt. impossible number of enrollments v. withdrawls: \n %s') % item['.url']
	else:
	    cntr += 1
	    rsult = datetime.timedelta(0,0,0)
	    for i in range(lene):
		try:
		    tmp = w[i]
    		except IndexError:
		    tmp = datetime.datetime.today()
		temp = tmp-e[i]
		#print temp,rsult
		rsult = temp+rsult
		#print '!'+rsult
	    #print "done?"
	    item[aggregate_fieldname] = rsult
    print "%s entries aggregated as '%s'" %(cntr, aggregate_fieldname)


def lastname_first(ql):
    aggregate_fieldname = 'lastname first'
    cntr = 0
    for x in ql:
	try:
	    xx = x['name']          
	except KeyError:
	    pass
	else:
	    cntr += 1
	    yy = xx.split(" ")
	    xx = yy[-1]+", "+" ".join(yy[:-1])
	    x[aggregate_fieldname] = xx

    print "%s entries aggregated as '%s'" %(cntr, aggregate_fieldname)


def age(ql):
    aggregate_fieldname = 'age'
    cntr = 0
    for x in ql:
	try:
	    dobs = x['dob']
	except KeyError:
	    pass
	else:
	    cntr += 1
	    now = datetime.datetime.today()
	    result = []
	    for dob in dobs:
		age = now - dob
		age = age.days / 365.
		result.append(age)
	    x[aggregate_fieldname] = result
    print "%s entries aggregated as '%s'" %(cntr, aggregate_fieldname)

