# routes.py – Software ACUITEE
# Copyright 2021 b<>com. All rights reserved.
# This software is licensed under the Apache License, Version 2.0.
# You may not use this file except in compliance with the license. 
# You may obtain a copy of the license at: 
# http://www.apache.org/licenses/LICENSE-2.0 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, 
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and 
# limitations under the License.



from application import app
from flask import render_template, request, json, Response, jsonify, session
import requests
from application.Global_objects import HPO_TERMS, HPO_OBO
import re
import datetime
from application.ParserSM import Normalize_Annotation_Format,Annotation_DF2List,Extract_HPO_Fr_StringMaching

# Setup the Flask-JWT-Extended extension
from flask_jwt_extended import JWTManager, create_access_token, decode_token
jwt = JWTManager(app)

@app.route("/")
@app.route("/index")
@app.route("/home")
def index():    
    return render_template("index.html", note_text=app.config["EXAMPLE_NOTE"])

@app.route("/note/put",methods=['POST'])
def generate_jwt():
    '''Takes a json request, returns a JWT token from the json content'''
    expires = datetime.timedelta(days=3)
    access_token = create_access_token(identity=request.json, expires_delta=expires)
    session['sourceid'] = request.json['sourceId']
    return access_token

@app.route("/note/<token>")
def verify_token(token):
    '''Takes the token in the url and returns a index page with the note loaded (identity validates the token)'''
    identity = decode_token(token)
    session['sourceid'] = identity['sub']['sourceId']
    return render_template("index.html", note_text=identity['sub']['note'])

@app.route("/note/savejson",methods=['POST'])
def SaveJson():
    path = app.config['JSON_REPO'] + '/' +  str(session['sourceid']) + '_data.json'
    with open(path, 'w') as f:
        json.dump(request.json, f)
    return {}

@app.route("/parse/bcomSM",methods=['POST','GET'])
@app.route("/note/parse/bcomSM",methods=['POST','GET'])
def ParseAC():
    note=request.json['note']
    _,HPO_terms=Extract_HPO_Fr_StringMaching(note)
    HPO_terms=Normalize_Annotation_Format(HPO_terms)
    HPO_terms=HPO_terms[["start","length","negated","patient","mult_CS","HPO_ID","HPO_Terms","score"]]
    annotations=Annotation_DF2List(HPO_terms)

    # add ratingInit and initialize it by rating. ratingInit will be useful to compare the term rating selected by
    # the clinician with the one proposed by the algorithm (ratingInit)
    # In addition, add a field called "validated" to each annotated phrase. This field will be used to indicate that 
    # the clinician has revised and validated the annotated phrase. 
    for i in range(len(annotations)):
        annotations[i]['validated']=False
        for j in range(len( annotations[i]['hpoAnnotation'])):
            annotations[i]['hpoAnnotation'][j]['ratingInit']=annotations[i]['hpoAnnotation'][j]['rating']

    # Postprocessing
    annotations=Annotations_Postprocessing(annotations)
    # save terms in the user session
    session['annoStruct'] = annotations
    
    return json.dumps(annotations)

def ParseAC_FromAPI():
    note=request.json['note']
    r = requests.post('http://localhost:5001/parser_SM', data = {'text':note})
    annotations=r.json()

    # add ratingInit and initialize it by rating. ratingInit will be useful to compare the term rating selected by
    # the clinician with the one proposed by the algorithm (ratingInit)
    # In addition, add a field called "validated" to each annotated phrase. This field will be used to indicate that 
    # the clinician has revised and validated the annotated phrase. 
    for i in range(len(annotations)):
        annotations[i]['validated']=False
        for j in range(len( annotations[i]['hpoAnnotation'])):
            annotations[i]['hpoAnnotation'][j]['ratingInit']=annotations[i]['hpoAnnotation'][j]['rating']

    # Postprocessing
    annotations=Annotations_Postprocessing(annotations)
    # save terms in the user session
    session['annoStruct'] = annotations

    return json.dumps(annotations)


@app.route("/update_Neg_MCS_Asc",methods=['POST','GET'])
@app.route("/note/update_Neg_MCS_Asc",methods=['POST','GET'])
def update_Neg_MCS_Asc():
    if session.get('annoStruct'):
        annotations= session['annoStruct']

        negated=request.json['negated']
        mult_CS=request.json['mult_CS']
        ascendant=request.json['ascendant']
        start=request.json['start']
        for anno in annotations:
            if anno['start']==start:                
                anno['negated']=negated
                anno['mult_CS']=mult_CS
                anno['ascendant']=ascendant
                break

        # Postprocessing
        annotations=Annotations_Postprocessing(annotations)
        # save terms in the user session
        session['annoStruct']=annotations
        return json.dumps(annotations)
    return {}

@app.route("/validateAnno",methods=['POST','GET'])
@app.route("/note/validateAnno",methods=['POST','GET'])
def validateAnno():
    if session.get('annoStruct'):
        annotations= session['annoStruct']
       
        start=request.json['start']
        for anno in annotations:
            if anno['start']==start:
                anno['validated']=True                
                break

        # Postprocessing
        annotations=Annotations_Postprocessing(annotations)
        # save terms in the user session
        session['annoStruct']=annotations
        return json.dumps(annotations)
    return {}

@app.route("/AddTerm_Mouse_Enter",methods=['POST','GET'])
@app.route("/note/AddTerm_Mouse_Enter",methods=['POST','GET'])
def AddTerm_Mouse_Enter():
    if not session.get('annoStruct'):
        session['annoStruct']=[]

    annotations= session['annoStruct']

    start=request.json['start']
    length=request.json['length']
    end=start+length-1

    # check if the new annotation range completely falls inside an existing one.
    # in this case, the user wants to decrease the annotation range. Therefore, 
    # we simply replace 'start' and 'length' of the existing annotation element
    # without adding a new element and without removing the HPO terms of the existing
    # element.
    rangeDecreasing=False
    for i in range(len(annotations)):
        start_i=annotations[i]['start']
        length_i=annotations[i]['length']
        end_i=start_i+length_i-1
        if (start>=start_i) and (end<=end_i):
            rangeDecreasing=True
            annotations[i]['start']=start
            annotations[i]['length']=length
            break        

    if not rangeDecreasing: # add new entry with empty list of HPO terms
        newEntry={'start': start, 'length': length, 'negated': False, 'ascendant': -1, 'mult_CS': False, 'validated':False,
            'hpoAnnotation': []}        
        annotations.append(newEntry)

    # Postprocessing
    annotations=Annotations_Postprocessing(annotations)
    
    session['annoStruct']=annotations
    return json.dumps(annotations)

def Annotations_Postprocessing(annotations):
    # 1- sort terms according to 'start'
    annotations = sorted(annotations, key=lambda k: k['start'])
    if len(annotations)<=1:
        return annotations
    # 2- merge the intersetced annotation ranges. The resultant merged annotation should contain all the HPO terms found
    #    in the merged ranges (without repetition). If there is a conflict between the 'negated', 'MCS' or 'ascendant' 
    #    attributes, we use the default values.
    rngIndexUnions=[]
    curRangeIndex=[]
    lastEnd=0
    for i in range(len(annotations)-1):
        curRangeIndex.append(i)
        
        start=annotations[i]['start']
        length=annotations[i]['length']
        end=start+length-1
        end=max(end,lastEnd)
        
        start_nxt=annotations[i+1]['start']
        length_nxt=annotations[i+1]['length']
        end_nxt=start_nxt+length_nxt-1
        
        if start_nxt>end:        
            rngIndexUnions.append(curRangeIndex)
            curRangeIndex=[]
        else:
            lastEnd=max(end,end_nxt)
            
        if i==len(annotations)-2:
            curRangeIndex.append(i+1)
            rngIndexUnions.append(curRangeIndex)
    
    # merge the intersected annotation ranges and the corresponding data
    annotations_Merged=[]
    for i in range(len(rngIndexUnions)):
        
        curDict={}
        if len(rngIndexUnions[i])==1:
            curDict=annotations[rngIndexUnions[i][0]]
            annotations_Merged.append(curDict)
        else:
            
            start=1000000 # initialization by a large value that is surely larger than the max possible 'start'
            end=0
            negated = True
            mult_CS = True
            validated=True
            modified = False
            ascendants=[]
            hpoAnnotationUnion=[]
            for j in range(len(rngIndexUnions[i])):
                start=min(start,annotations[rngIndexUnions[i][j]]['start'])
                end=max(end,annotations[rngIndexUnions[i][j]]['start']+annotations[rngIndexUnions[i][j]]['length'])
                curAnno=annotations[rngIndexUnions[i][j]]['hpoAnnotation']
                if len(curAnno):
                    modified = True
                    negated=negated&annotations[rngIndexUnions[i][j]]['negated']
                    mult_CS=mult_CS&annotations[rngIndexUnions[i][j]]['mult_CS']
                    validated=validated&annotations[rngIndexUnions[i][j]]['validated']
                    ascendants.append(annotations[rngIndexUnions[i][j]]['ascendant'])
                
                # flatten the set of annotations
                for k in range(len(curAnno)):
                    hpoAnnotationUnion.append(curAnno[k])
            
            if not modified:
                negated = False
                mult_CS = False
                validated= False

            curDict['start']=start
            length=end-start
            curDict['length']=length        
            curDict['negated']=negated
            curDict['mult_CS']=mult_CS
            curDict['validated']=validated
            if len(ascendants):
                curDict['ascendant']=max(set(ascendants), key=ascendants.count)
            else:
                curDict['ascendant']=-1
            
            # keep only unique IDs in hpoAnnotations
            
            # for now , just filter out the duplicates
            hpoAnnotation=list({v['hpoId']:v for v in hpoAnnotationUnion}.values())
            
            curDict['hpoAnnotation']=hpoAnnotation
            annotations_Merged.append(curDict)
    return annotations_Merged

@app.route("/Search_Terms",methods=['POST','GET'])
@app.route("/note/Search_Terms",methods=['POST','GET'])
def Search_Terms():
    query=request.json['query']
    matched_terms=Search_HPO_Terms(query)
    return json.dumps(matched_terms)

def Search_HPO_Terms(query):
    query = query.lower()
    termCounter=0
    matched_terms=[]
    for term in HPO_TERMS:
        res = re.search(query, term[0])
        if res is not None:
            termCounter+=1
            matched_terms.append({'ID':str(term[1]),'term':str(term[0])})
            if termCounter>=10:
                break    
    return matched_terms


@app.route("/Remove_HPO_Term",methods=['POST','GET'])
@app.route("/note/Remove_HPO_Term",methods=['POST','GET'])
def Remove_HPO_Term():
    start=int(request.json['start'])
    hpoID=request.json['hpoId']
    annotations= session['annoStruct']

    # delete the indicated term
    for i in range(len(annotations)):
        start_i=annotations[i]['start']
        
        if start==start_i:
            curAnno=annotations[i]['hpoAnnotation']
            for j in range(len(curAnno)):
                if curAnno[j]['hpoId']==hpoID:
                    del annotations[i]['hpoAnnotation'][j]
                    break
            break

    # write the updated annotations to the session
    session['annoStruct']=annotations
    return json.dumps(annotations)


@app.route("/Add_HPO_Term",methods=['POST','GET'])
@app.route("/note/Add_HPO_Term",methods=['POST','GET'])
def Add_HPO_Term():
    start=int(request.json['start'])
    hpoID=request.json['hpoId']
    hpoTerm=request.json['hpoTerm']
    annotations= session['annoStruct']

    newDict={'hpoId': hpoID, 'hpoName': hpoTerm, 'rating': 3, 'ratingInit': 0}

    termExists=False

    # add the indicated term (if not exists)
    for i in range(len(annotations)):
        start_i=annotations[i]['start']
        
        if start==start_i:
            curAnno=annotations[i]['hpoAnnotation']
            for j in range(len(curAnno)):
                if curAnno[j]['hpoId']==hpoID: 
                    termExists=True
            if not termExists: # if the term already exists; do nothing
                annotations[i]['hpoAnnotation'].append(newDict)
            break

    # write the updated annotations to the session
    session['annoStruct']=annotations
    return json.dumps(annotations)

@app.route("/getHpoTermDetails",methods=['POST','GET'])
@app.route("/note/getHpoTermDetails",methods=['POST','GET'])
def getHpoTermDetails():
    hpoID=request.json['hpoId']
    hpoTerm=HPO_OBO[hpoID]
    synonyms=[s.description for s in hpoTerm.synonyms]
    hierarchy=[s.name for s in hpoTerm.superclasses(10)]
    termDetails={'termDetails': {"ID":hpoTerm.id,"name": hpoTerm.name, "Def":hpoTerm.definition,"Synonyms": synonyms, "Hierarchy":hierarchy}}
    return json.dumps(termDetails)

@app.route("/get_annotation_results",methods=['GET'])
@app.route("/note/get_annotation_results",methods=['GET'])
def get_annotation_results():
    if not session.get('annoStruct'):
        session['annoStruct']={}
    annotations= session['annoStruct']
    return json.dumps(annotations)

@app.route("/updateTermRating",methods=['POST','GET'])
@app.route("/note/updateTermRating",methods=['POST','GET'])
def updateTermRating():
    start=int(request.json['start'])
    hpoID=request.json['hpoId']
    starNum=int(request.json['starNum'])

    annotations= session['annoStruct']
    # modify the rating 
    for i in range(len(annotations)):
        start_i=annotations[i]['start']
        
        if start==start_i:
            curAnno=annotations[i]['hpoAnnotation']
            for j in range(len(curAnno)):
                if curAnno[j]['hpoId']==hpoID:
                    curRating=annotations[i]['hpoAnnotation'][j]['rating']
                    if curRating==starNum:                        
                        if starNum==1:
                            annotations[i]['hpoAnnotation'][j]['rating']=0
                    else:
                        annotations[i]['hpoAnnotation'][j]['rating']=starNum
                    break
            break

    # write the updated annotations to the session
    session['annoStruct']=annotations
    return json.dumps(annotations)

@app.route("/RemoveAnnotationUnit",methods=['POST','GET'])
@app.route("/note/RemoveAnnotationUnit",methods=['POST','GET'])
def RemoveAnnotationUnit():
    if session.get('annoStruct'):
        annotations= session['annoStruct']

        start=request.json['start']        
        
        for i in range(len(annotations)):
            start_i=annotations[i]['start']
            if start==start_i:
                del annotations[i]                
                break
        # Postprocessing       
        annotations=Annotations_Postprocessing(annotations)        
        # save terms in the user session
        session['annoStruct']=annotations
        return json.dumps(annotations)
    return {}
