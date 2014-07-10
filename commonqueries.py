import queries as q

def enrolled_families():
    QL = q.QueryList()
    QL.query('is_enrolled')
    QL2 = QL.convert_to_parents()
    QL2.output_as_csv('name, phone, email, address', outfile = './output/enrolled_families.csv')
    QL2.output_as_html('.link, name, phone, email, address', outfile = './output/enrolled_families.html')
    output_addresses(QL2)

def enrolled_student_information():
    QL = q.QueryList()
    QL.query('is_enrolled')
    q.age(QL)
    q.time_enrolled(QL)
    q.lastname_first(QL)
    QL.sort('lastname first')
    QL.output_as_csv('lastname first, age, enrolled, days enrolled, allergies', outfile = './output/enrolled_student_information.csv')
    QL.output_as_html('.link, lastname first, age, enrolled, days enrolled, allergies', outfile = './output/enrolled_student_information.html')

def alltime_student_information():
    QL = q.QueryList()
    QL.query('enrolled_exists')
    q.age(QL)
    q.time_enrolled(QL)
    q.lastname_first(QL)
    QL.sort('lastname first')
    QL.output_as_csv('lastname first, age, enrolled, days enrolled', outfile = './output/alltime_student_information.csv')
    QL.output_as_html('.link, lastname first, age, enrolled, days enrolled', outfile = './output/alltime_student_information.html')

def output_addresses(QL,outfile='./output/addresses.txt'):
    with open(outfile,'wb') as writer:
        for item in QL:
            name = item['name']
            try:
                address = item['address']
            except KeyError:
                address = None
            if address:
                address = ' '.join(address).replace('|','\n')
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

