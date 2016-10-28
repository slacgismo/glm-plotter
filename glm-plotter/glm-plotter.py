"""
    JAC - jdechalendar@stanford.edu
    July 15, 2016
    Flask controller for glm-plotter app
"""
from flask import Flask, render_template, request, session
import os, json, random
import myParser

app = Flask(__name__)

# route for the index page - this is the page that is visible to the user
@app.route("/", methods=['GET','POST'])
def index():
#    print(session)
    if request.method == 'POST':
        if 'fixedNodes' in request.files and request.files['fixedNodes'] and request.files['fixedNodes'].filename.rsplit('.', 1)[1] == 'csv':
            print('Reading the csv file')
            session['csv']=1
            fullfilename = os.path.join(app.config['UPLOAD_FOLDER'], "curr.csv")
            request.files['fixedNodes'].save(fullfilename)
        if 'glm_file' in request.files and request.files['glm_file'] and request.files['glm_file'].filename.rsplit('.', 1)[1] == 'glm':
            print('Reading the glm file')
            session.clear()
            session['glm_name'] = request.files['glm_file'].filename            
            fullfilename = os.path.join(app.config['UPLOAD_FOLDER'], "curr.glm")
            request.files['glm_file'].save(fullfilename)
    return render_template("index.html")

# route for the data that is used to plot the network
# information about nodes/edges of the graph as well as positions for fixed
# nodes
# this route is accessed by the plotNetwork.js script
@app.route("/data/network")
def glm():
    glmFile = os.path.join(app.config['UPLOAD_FOLDER'], "curr.glm")
    csvFile = os.path.join(app.config['UPLOAD_FOLDER'], "curr.csv")
    if 'csv' in session and session['csv'] and os.path.isfile(csvFile):
        fixedNodesJSON = parseFixedNodes(csvFile)
    else:
        fixedNodesJSON = '{"names":[], "x":[], "y":[]}'
    if os.path.isfile(glmFile):
        objs,modules,commands = myParser.readGLM(glmFile)
        graphJSON = myParser.createD3JSON(objs)
    else:
        graphJSON = '{"nodes":[],"links":[]}'
    if 'glm_name' in session:
        glm_name = session['glm_name']
    else:
        glm_name = ''
    JSONstr = '{"file":"' + glm_name + '","graph":' + graphJSON + ',"fixedNodes":' + fixedNodesJSON +'}'
    return JSONstr

# route for the data that is used to plot time series
# this route is accessed by the plotTS.js script
@app.route("/data/ts/<nodeID>")
def ts_node(nodeID):
    fileNm = 'uploads/' + str(nodeID) + '.csv'
    if os.path.isfile(fileNm):
        return myParser.preprocessTS(fileNm)
    else:
        return ""

# route to generate a list of all the timestamps in the dataset
@app.route("/data/ts/timestamps")
def generate_timestamps():
    # TODO
    #return simulation timestamps that slider will use to initialize its range
    return "23000"

# route to generate data for all objects at one point in time
# this route is accessed by the plotTS.js script
@app.route("/data/timestamp/<timestamp>")
def global_state(timestamp):
    # TODO
    #return myParser.getLineValues(timestamp)
    # dummy data for testing
    glmFile = os.path.join(app.config['UPLOAD_FOLDER'], "curr.glm")
    objs, _, _ = myParser.readGLM(glmFile)
    bla = "lineID,currentValue\n"
    link_type = ['overhead_line','switch','underground_line','regulator','transformer', 'triplex_line','fuse']
    link_objs = [obj for obj in objs if obj['class'] in link_type]
    for link in link_objs:
        bla += link['name'] + ',' + str(round(1000*random.random())/10) + '\n'
    # if int(timestamp) < 600:
    #     bla = "lineID,currentValue\nline50to51,0\nline51to151,0\nline49to50,0\nline47to49,0\nline47to48,0\n"
    # else:
    #     bla = "lineID,currentValue\nline50to51,100\nline51to151,0\nline49to50,100\nline47to49,100\nline47to48,0\n"
    return bla

app.config['UPLOAD_FOLDER'] = 'uploads'

def parseFixedNodes(nodesFile):
    with open(nodesFile) as fr:
        lines = fr.readlines()
    names=[]
    x=[]
    y=[]
    for line in lines:
        bla = line.split(',')
        if len(bla) == 3:
            names.append(bla[0])
            x.append(float(bla[1]))
            y.append(float(bla[2]))
    return json.dumps({'names':names,'x':x,'y':y})

if __name__ == "__main__":
    app.secret_key = 'B0er23j/4yX R~XHH!jmN]LWX/,?Rh'
    app.run(debug=True)