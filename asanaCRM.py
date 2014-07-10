import secrets
import asana.asana as asana
import parser
import pickle
import datetime
from os import rename,path
from collections import Counter

strptime = datetime.datetime.strptime

def pickle_asana_project():
    #load API
    asana_api = asana.AsanaAPI(secrets.api_key, debug=True)

    workspace,project = secrets.workspace,secrets.project

    #get ready by finding the id #'s of the hardcoded workspace and project
    workspaces = asana_api.list_workspaces()
    completed = False
    for ws in workspaces:
        print ws['name'],workspace
        if ws['name'].lower() == workspace.lower():
          completed = True
          workspace = ws['id']
          break

    if completed == False:
      print "These are all the workspaces I found: \n %s" % workspaces
      raise asana.AsanaException('Workspace "%s" not found' % workspace)

    projects = asana_api.list_projects(workspace,include_archived=False)
    completed = False
    for ps in projects:
        if ps['name'].lower() == project.lower():
          completed = True
          project = ps['id']
          break

    if completed == False:
        print "These are all the projects I found: \n %s" % projects
        raise asana.AsanaException('Project "%s" not found' % project)

    #Now, get all the tasks that are within the hardcoded project
    tasks = asana_api.get_project_tasks(project,include_archived=True)
        
    #harvest data from every task and store it in a dictionary to be pickled
    result=[]
    for task in tasks:
        #metadata have '.'s before them to prevent collision with parser keywords
        meta_dict = {}
        meta_dict['.name'] = task['name']
        meta_dict['.id'] = task['id']        
        t = asana_api.get_task(task['id'])
        meta_dict['.created'] = strptime(t['created_at'].split('.')[0],"%Y-%m-%dT%H:%M:%S")
        meta_dict['.url'] =  "https://app.asana.com/0/%s/%s/" % (workspace,task['id'])
        meta_dict['.link'] = "<a href='%s' target='_blank'>%s</a>" % (meta_dict['.url'],meta_dict['.name'])

        list_of_individuals = parser.to_dictionary(t['notes'])
        list_of_individuals[0].update(meta_dict)
        list_of_individuals[0].update({'.notes':t['notes'],'.parent':True})

        for item in list_of_individuals:
            item.update(meta_dict)
                
        result.extend(list_of_individuals)

    backup_filename = path.join(secrets.pickle_folder,datetime.datetime.now().isoformat()[:16]+'.pickle')

    try:
        rename(secrets.pickle_file,backup_filename)
    except OSError:
        #File did not exist, so don't back it up!
        pass
        
    with open(secrets.pickle_file,'wb') as fp:
        pickle.dump(result,fp)

def build_error_page():
    '''build an html page with links to asana tasks and the errors associated with them'''
    counter = Counter()
    with open(secrets.pickle_file,'rb') as fp:
      data = pickle.load(fp)
 
    with open(secrets.error_html,'wb') as fp:
      fp.write('<html><body>')
      for item in data:
        counter.update(item.keys())
        try:
            errors =  item['errors']
        except KeyError:
            pass
        else:
            #print item['.url']
            name = item['name']
            url = item['.url']
            fp.write('<a href="%s" target="_blank">%s</a> had the following errors: <br/>' % (url,name))
            for error in errors:
              fp.write('&nbsp; &nbsp; %s <br/>' % error)
      fp.write('<p>Key Frequencies (check for markup inconsistencies):</p>')
      for xx in counter.most_common():
        fp.write('&nbsp; &nbsp; %s : %s <br/>'%xx)
      fp.write('</body></html>')
 


if __name__ == '__main__':
    print "Pickling project..."
    pickle_asana_project()
    print "Building error page as %s" % secrets.error_html
    build_error_page()
    print "Done!"
