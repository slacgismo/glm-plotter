"""
    JAC - jdechalendar@stanford.edu
    July 15, 2016
    Parsers for glm-plotter app 
"""
import pandas as pd
import os
def readGLM(iFile,verb=0):
    """
        Main function to parse GLM files
        Modified July 12, 2016 - the returned objs are now a list
        Use list comprehensions to extract list of objects of a given class
    """
    with open(iFile) as f:
        lines = f.readlines()
    modules = set()
    objs = []
    commands=[]
    iLine = -1
    while True:
        iLine +=1
        if iLine>len(lines)-1:
            break
        if lines[iLine].strip().startswith('object'):
            read_objs,iLine=readObj(iLine,lines)
            for obj in read_objs:
                objs.append(obj)
        if lines[iLine].startswith('module'):
            modules.add(lines[iLine][7:].split('{')[0].strip(';').strip())
        if lines[iLine].startswith('#'):
            commands.append(lines[iLine])
    if verb:
        classList = [obj['class'] for obj in objs]
        countClass = {x:classList.count(x) for x in classList}
        print('Objects classes: ' + str([str(a[0]) +': ' +str(a[1]) for a in zip(countClass.keys(),countClass.values())]))
        print('Modules: ' + str(modules))
    # post processing step to make sure the parent fields are correct
    # this was added to deal with the old glm syntax
    # the startLine and name fields are always there, the name_oldGLM is optional
    startLines = [obj['startLine'] for obj in objs]
    names = [obj['name'] for obj in objs]
    names_oldGLM = [obj['name_oldGLM'] if 'name_oldGLM' in obj else '' for obj in objs]
    for obj in objs:
        if 'parent' in obj:
            if obj['parent'] not in names:
                if obj['parent'] in names_oldGLM:
                    parentObjID = names_oldGLM.index(obj['parent'])
                    obj['parent'] = objs[parentObjID]['name']
                elif obj['parent'] in startLines:
                    parentObjID = startLines.index(obj['parent'])
                    obj['parent'] = objs[parentObjID]['name']
                else:
                    raise ValueError("Cannot find this child's parent!")

    return objs,modules,commands

def readObj(startLine,lines,parent=''):
    """
        Read an object or objects (note that they can be nested)
        In old GLM files, there can be an object identifier given after a colon in the opening statement, or no name
        In order of preference, we choose as our name the name, the object identifier (name_oldGLM) and the line of the opening statement
        The startLine and name fields are always there, the name_oldGLM is optional
    """
    obj = [dict()]
    currLine = startLine
    if lines[currLine].strip().startswith('object'):
        objClass = lines[currLine][7:].split('{')[0].split(':')
        obj[0]['class']=objClass[0].strip()
        obj[0]['startLine']=str(currLine)
        if len(objClass)>1 and objClass[1].strip(): # old syntax for glm files - there can be an id for the object after a colon
            # consider this is the name for now. If there is a name later on it will be overwritten
            obj[0]['name_oldGLM'] = objClass[1].strip()
        if len(parent)>0:
            obj[0]['parent']=parent
        while True:
            currLine += 1
            if lines[currLine].find('}')>-1 and not lines[currLine].find('{')>-1:
                break
            if lines[currLine].strip().startswith('object'):
                if 'name' in obj[0]:
                    child,currLine = readObj(currLine,lines,parent=obj[0]['name'])
                    currLine=currLine
                    obj.extend(child)
                elif 'name_oldGLM' in obj[0]:
                    child,currLine = readObj(currLine,lines,parent=obj[0]['name_oldGLM'])
                    currLine=currLine
                    obj.extend(child)
                else:
                    child,currLine = readObj(currLine,lines,parent=obj[0]['startLine'])
                    currLine=currLine
                    obj.extend(child)
            else:
                if not lines[currLine].strip().startswith('//'):
                    tmp=lines[currLine].split(';')[0].split()
                    if len(tmp)>0:
                        if len(tmp)==2:
                            obj[0][tmp[0]]=tmp[1].strip('"')
                        elif len(tmp)==3: #tmp[0].lower().startswith('rated') or tmp[0].lower().startswith('reconnect_time'): # second case means there can be a unit
                            # we expect a unit
                            obj[0][tmp[0]]=tmp[1:]
                        else:
                            print(str(currLine) + ' - Not expected')
                            print(lines[currLine])
    for a in obj:
        if 'name' not in a:
            if 'name_oldGLM' in a:
                a['name']=a['name_oldGLM']
            else:
                a['name']=a['startLine']       
    return obj,currLine

def readClock(lines,currLine):
    """
        This function reads the clock in the GLM file
    """
    while True:
        currLine+=1
        if lines[currLine].find('}')>-1 and not lines[currLine].find('{')>-1:
            break
        if lines[currLine].strip().startswith('timezone'):
            timezone = lines[currLine].strip().split(';')[0].strip('timezone ').strip('"')
        if lines[currLine].strip().startswith('starttime'):
            tmp = lines[currLine].strip().split(';')[0].strip('starttime ')
            tmp=pd.to_datetime(tmp)
            starttime=tmp
        if lines[currLine].strip().startswith('stoptime'):
            tmp = lines[currLine].strip().split(';')[0].strip('stoptime ')
            tmp=pd.to_datetime(tmp)
            stoptime=tmp
    return timezone,starttime,stoptime

def getObjs(objs,attr,val=''):
    """
        one liner to get list of all the objects whose attribute attr has value val
        Example call: getObjs(objs, 'class', 'load')
    """
    if val:
        return [obj for obj in objs if attr in obj and obj[attr]==val];
    else:
        return [obj for obj in objs if attr in obj];

def getAieul(objs,name):
    parent = [obj for obj in objs if obj['name']==name]
    if len(parent)==0:
        parent = [obj for obj in objs if 'name_oldGLM' in obj and obj['name_oldGLM']==name]
    if len(parent)==0:
        parent = [obj['parent'] for obj in objs if obj['startLine']==name]
    if len(parent)!=1:
        raise ValueError('The name to object relation should be bijective!')
    if 'parent' in parent[0]:
        parent = getAieul(objs,parent[0]['parent'])
    return parent;

def createGraph(objs, node_type=['node','load','meter', 'triplex_meter','triplex_node'], link_type=['overhead_line','switch','underground_line','regulator','transformer', 'triplex_line','fuse']):
    link_objs = [obj for obj in objs if obj['class'] in link_type]
    links=list(zip([getAieul(objs,link['from'])[0]['name'] for link in link_objs],
                   [getAieul(objs,link['to'])[0]['name'] for link in link_objs],[link['class'] for link in link_objs],
                   [link['name'] for link in link_objs]))
    parent_objs = [obj for obj in objs if 'parent' not in obj]
    node_objs = [obj for obj in parent_objs if obj['class'] in node_type]
    #children I want to plot
    child_type = ['diesel_dg','capacitor']
    children=dict([(obj['parent'], obj['class']) for obj in objs if obj['class'] in child_type])
    # find unique nodes
    unique_nodes = list(set([n1 for n1, n2,_,_ in links] + [n2 for n1, n2,_,_ in links]+[nd['name'] for nd in node_objs]))
    if len(unique_nodes) > len(node_objs):
        print('I had to add ' + str(len(unique_nodes)-len(node_objs)) + ' nodes to draw the links - something is off')
    classNm = [next((obj['class'] for obj in node_objs if obj["name"] == nd),'') for nd in unique_nodes]
    child = [children[nd] if nd in children else '' for nd in unique_nodes]

    return unique_nodes, links, child, classNm

def createD3JSON(objs,fileNm_out=''):
    """
        This function creates a json file that will be used for plotting the GLM objects by the D3 force algorithm
        We use hardcoded decisions of which links and nodes should be plotted
        See GLMtoJSON notebook to change this
        Inputs are the objs object from the readGLM function and a file to write the output to
        If no file name is provided, returns the json string
    """

    # define links I want to plot
    link_type = ['overhead_line','switch','underground_line','regulator','transformer', 'triplex_line','fuse']
    
    # define nodes I want to plot
    node_type = ['node','load','meter', 'triplex_meter','triplex_node']
    
    unique_nodes, links, child, classNm = createGraph(objs, node_type, link_type)

    JSONstr = ''
    JSONstr += '{\n  "nodes":[\n'
    if len(unique_nodes) > 0:
        for iNode in range(len(unique_nodes)-1):
            JSONstr += '    {"name":"' + unique_nodes[iNode]\
            + '","classNm":"' + str(classNm[iNode])\
            + '","child":"' + str(child[iNode])\
            + '"},\n'
        JSONstr += '    {"name":"'+ unique_nodes[len(unique_nodes)-1]\
        + '","classNm":"' + str(classNm[len(unique_nodes)-1])\
        + '","child":"' + str(child[len(unique_nodes)-1])\
        + '"}\n'
    JSONstr+='  ],\n "links":[\n'
    if len(links) > 0:
        for iLink in range(len(links)-1):
            JSONstr +='    {"source":'+ str(unique_nodes.index(links[iLink][0]))\
            + ',"target":'+ str(unique_nodes.index(links[iLink][1]))\
            + ',"linkType":"'+ links[iLink][2]\
            + '","linkName":"'+ links[iLink][3]\
            + '"},\n'
        JSONstr += '    {"source":'+ str(unique_nodes.index(links[len(links)-1][0]))\
        + ',"target":'+ str(unique_nodes.index(links[len(links)-1][1]))\
        + ',"linkType":"'+ links[len(links)-1][2]\
        + '","linkName":"'+ links[len(links)-1][3]\
        + '"}\n'
    JSONstr += '  ]\n}'
    if fileNm_out:
        with open(fileNm_out,'w') as f:
            f.write(JSONstr)
        JSONstr='' # if we wrote to file, don't return it
    return JSONstr

def preprocessTS(fileNm):
    """
        This function reads csv output data from of GridLab-D simulation and
        preprocesses it to make it easy to ready using the d3.csv function.
    """
    myStr = ''
    with open(fileNm, 'r') as fr:
        data = fr.readlines()
    dataFirstLine = 0
    dataLines = [d for d in data if d[0] is not '#']
    headerLines = [d for d in data if d[0] is '#']
    dataLines.insert(0,headerLines[-1][2:]) # remove the # and the first space
    print(''.join(dataLines))
    return ''.join(dataLines)