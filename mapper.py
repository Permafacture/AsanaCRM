'''
This file is deprecated.  pygmaps_ng should replace whatever
it is I was doing here before'''

deprecated #cause an error

#!/usr/bin/python
from pygeocoder import Geocoder
from csv import DictReader, DictWriter
from queries import QueryList
from collections import OrderedDict
import brewer2mpl

working_folder = "./maps/"

#these two are logically bound together, though not explicit
commands = ['enrolled_exists', 'visited_exists','dob_exists', 'address_exists']
colors = brewer2mpl.get_map('RdPu', 'Sequential', len(commands)).hex_colors
			

def get_addresses():
    '''make a csv and html of the query results of groups we have addresses for (for map coordinates)'''
    QL = QueryList()
    last_time = set()

    #list of subsets, from most specific to most broad 
    for command in commands:
	#run the query and then remove those that were already in the smaller set
	QL.reset()
	QL.query(command)
        temp = QL.convert_to_parents()
        temp.query('address_exists')

	for i,x in enumerate(temp):
	    x = x['.id']
 	    if x in last_time:
		temp[i] = 'xxx'
            last_time.add(x)
	#there's gotta be a better way to remove all occurances of 'xxx'...
	while 1:
	    try:
	      temp.remove('xxx')
	    except ValueError:
	      break
        temp.output_as_csv('name, address', query=False, outfile = '%s%s.csv' % (working_folder, command))
        temp.output_as_html('.link, name, address', outfile = '%s%s.html' % (working_folder, command))



def geocode_file(verbose=False):
    '''return a list of dictionaries with lat, long, name and color.
    For dubugging, you may want to decouple this from whatever uses the result
    with a pickle.'''
  
    fuzz = True

    if not fuzz:
	print "WARNING: position is not fuzzed and results may be a privacy concern"

    result = []
    for i,command in enumerate(commands):
        with open('%s%s_data.csv' % (working_folder,command) ,'wb') as r:
	    writer = DictWriter(r,delimiter='\t',fieldnames=('latitude','longitude'))
	    writer.writeheader()
	    with open('%s%s.csv' % (working_folder,command) ,'rb') as f:
		reader=DictReader(f,delimiter='\t')
		for item in reader:
		    addr = item['address'].replace('|',' ')
		    print "working on ", addr
		    geo = Geocoder.geocode(addr)
		    temp = {}
		    if fuzz:
			temp['latitude'] = '%.3f' % geo.latitude
			temp['longitude'] = '%.3f' % geo.longitude
		    else:
			temp['latitude'] = geo.latitude
			temp['longitude'] =  geo.longitude
		    writer.writerow(temp)
		    #temp['name']=item['name']
		    temp['color'] = colors[i]
	            result.append(temp)
    if verbose:
       print result
    return result

def mapit(pointdict):
    from maps.pygmaps import maps

    Austin = Geocoder.geocode('Clearview Sudbury School, Austin Texas')

    mymap = maps(Austin.latitude,Austin.longitude,16)
    for item in pointdict:
	mymap.addpoint(float(item['latitude']),float(item['longitude']),item['color'])

    mymap.draw('./maps/all_contacts.html')

if __name__ == '__main__':
  mapit(geocode_file(verbose=False))
