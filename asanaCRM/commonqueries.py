'''Queries I run all the time, with html and csv outputs.  
   Use these as examples.'''

import queries as q
import os.path as path
out_dir = "/home/elbiot/Dropbox/Clerkship Documents/Records/asana"

def enrolled_student_information():
    QL = q.QueryList()        #create an unfiltered QuerySet
    QL.query('is_enrolled')   #filter 
    q.age(QL)                 #process QL to add calculated age based on DOB
    q.time_enrolled(QL)       #add time enrolled calculated from enrolled and withdrew
    q.lastname_first(QL)      #add "lastname, firstname" representation of name 
    QL.sort('lastname first') #sort by "lastname, firstname"
    #Different information is wanted for csv and html outputs
    QL.output_as_csv('lastname first, age, enrolled, days enrolled, directory, photos, allergies', 
                     outfile = path.join(out_dir,'enrolled_student_information.csv'))
    QL.output_as_html('.link, lastname first, age, enrolled, days enrolled, directory, photos, allergies', 
                     outfile = path.join(out_dir, 'enrolled_student_information.html'))

def enrolled_families():
    QL = q.QueryList()
    QL.query('is_enrolled')   #select only enrolled individuals
    QL2 = QL.convert_to_parents()  #create QuerySet that is the parents of those
    QL2.output_as_csv('name, phone, email, address', 
                      outfile = path.join(out_dir,'enrolled_families.csv'))
    QL2.output_as_html('.link, name, phone, email, address', 
                      outfile = path.join(out_dir,'enrolled_families.html'))
    output_addresses(QL2)

def alltime_student_information():
    QL = q.QueryList()
    #ratehr than is_enrolled, get those that have ever been enrolled
    QL.query('enrolled_exists')
    q.age(QL)
    q.time_enrolled(QL)
    q.lastname_first(QL)
    QL.sort('lastname first')
    QL.output_as_csv('lastname first, age, enrolled, days enrolled',
                      outfile = path.join(out_dir,'alltime_student_information.csv'))
    QL.output_as_html('.link, lastname first, age, enrolled, days enrolled', 
                      outfile = path.join(out_dir,'alltime_student_information.html'))

def output_addresses(QL,outfile=path.join(out_dir,'addresses.txt')):
    valid_ids = {item['.id'] for item in QL}
    valid_entries = [item for item in q.database() if item[0]['.id'] in valid_ids]
    with open(outfile,'wb') as writer:
        for family in valid_entries:
            name = ''
            address = ''
            for member in family:
                if 'name' in member:
                    name += member['name']+', '
                if 'address' in member:
                    address += ''.join(member['address'])+'\n'
            if address:
                address = address.replace('|','\n')
                writer.write('\n'+name+'\n')
                writer.write(address+'\n')
            else:
                print "%s doesn't have an address" % name


if __name__ == '__main__':
    import os, time
    from secrets import pickle_file

    enrolled_families()
    enrolled_student_information()
    alltime_student_information()

    s = time.ctime(os.stat(pickle_file).st_mtime)
    print '\n\n*********\n\nThese reports are using data from %s\nIf this is too old, re-run asanaCRM.py to update the pickle\n\n*********\n\n' % s
