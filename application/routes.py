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


import os
from application import app
from flask import render_template, request, json, session
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
    '''Render a default page for testing'''
    return render_template("index.html", note_text=app.config["EXAMPLE_NOTE"])

@app.route("/note/put",methods=['POST'])
def generate_jwt():
    '''Takes a json request, returns a JWT token from the json content'''
    path = app.config['JSON_REPO'] + '/' +  str(request.json['sourceId']) + '_note.txt'
    with open(path, 'w') as f:
        f.write(request.json['note'])
    expires = datetime.timedelta(days=3)
    del request.json['note']
    access_token = create_access_token(identity=request.json, expires_delta=expires)
    return access_token

@app.route("/note/<token>")
def verify_token(token):
    '''Takes the token in the url and returns a index page with the note loaded (identity validates the token)'''
    identity = decode_token(token)
    session['annotatorId'] = identity['sub']['annotator']
    session['sourceId'] = identity['sub']['sourceId']
    path = app.config['JSON_REPO'] + '/' +  str(session['sourceId']) + '_note.txt'
    with open(path, 'r') as f:
        session['note'] = f.read()
    os.remove(path)
    return render_template("index.html", note_text=session['note'])

def Concerned_Person_str2num(AscStr):
    predef_pat={'Pt1':0,'Pt2':1,'Mat':2,'Par':3,'Oth':4}
    return predef_pat[AscStr]

def ENLIGHTOR_results_normalization(annotations_list):
    for ann in annotations_list:
        ann["concerned_person"]=Concerned_Person_str2num(ann["concerned_person"])
    return annotations_list

@app.route("/note/savejson",methods=['POST'])
def save_json():
    '''Save annotation in json file on disk'''
    path = app.config['JSON_REPO'] + '/' +  str(session['sourceId']) + '_data.json'
    with open(path, 'w') as f:
        json.dump(request.json, f)
    return {}

@app.route("/parse/bcom",methods=['POST','GET'])
@app.route("/note/parse/bcom",methods=['POST','GET'])
def Parse():
    '''Parse the given note'''
    note=request.json['note']
    bParser_StrMatch=request.json['bStrMatch']
    bParser_ENLIGHTOR=request.json['bENLIGHTOR']

    annotations_SM=[]
    annotations_EL=[]

    if bParser_ENLIGHTOR:
        print("Parsing with ENLIGHTOR...")
        try:            
            r = requests.post('http://172.30.5.255:5001/parser_ENLIGHTOR', data = {'text':note}) # when connecting the parser to the docker network of acuitee, use this IP address
            annotations_EL=r.json()
            annotations_EL=ENLIGHTOR_results_normalization(annotations_EL)
            print(annotations_EL)
        except requests.exceptions.RequestException as e:
            print("ENLIGTHOR WEB API Unreachable!")
            print(e)
            """
            # some virtual annotations are provided here for testing mutli-parser annotation. Delete them when the ENLIGHTOR web API is stable.
            annotations_EL=[
            {'start': 1466, 'length': 6, 'negated': False, 'concerned_person': 'Pt1', 'mult_CS': False, 'hpoAnnotation': [{'hpoId': 'HP:0100300', 'hpoName': 'desmin bodies', 'rating': '0.6619'}]}, 
            {'start': 499, 'length': 82, 'negated': False, 'concerned_person': 'Pt1', 'mult_CS': False, 'hpoAnnotation': [{'hpoId': 'HP:0010549','hpoName': 'weakness due to upper motor neuron dysfunction', 'rating': '0.6778'}, {'hpoId': 'HP:0003397', 'hpoName': 'generalized hypotonia due to defect at the neuromuscular junction', 'rating': '0.6763'}, {'hpoId': 'HP:0011692', 'hpoName': 'supraventricular tachycardia with a concealed accessory pathway on the right free wall', 'rating': '0.6706'}, {'hpoId': 'HP:0032886', 'hpoName': 'focal impaired awareness cognitive seizure with expressive dysphasia/aphasia', 'rating': '0.6674'}, {'hpoId': 'HP:0011691', 'hpoName': 'supraventricular tachycardia with a concealed accessory pathway on the left free wall', 'rating': '0.6655'}]}, 
            {'start': 1728, 'length': 160, 'negated': False, 'concerned_person': 'Pt1', 'mult_CS': False, 'hpoAnnotation': [{'hpoId': 'HP:0032788', 'hpoName': 'focal impaired awareness autonomic seizure with palpitations/tachycardia/bradycardia/asystole', 'rating': '0.6834'}, {'hpoId': 'HP:0032861', 'hpoName': 'focal non-convulsive status epilepticus with impairment of consciousness', 'rating': '0.6785'}, {'hpoId': 'HP:0032869', 'hpoName': 'focal non-convulsive status epilepticus without impairment of consciousness', 'rating': '0.6777'}, {'hpoId': 'HP:0032793', 'hpoName': 'focal impaired awareness cognitive seizure with receptive dysphasia/aphasia', 'rating': '0.6742'}, {'hpoId': 'HP:0032662', 'hpoName': 'focal-onset seizure evolving into bilateral convulsive status epilepticus', 'rating': '0.6732'}]}, 
            {'start': 662, 'length': 132, 'negated': False, 'concerned_person': 'Pt1', 'mult_CS': False, 'hpoAnnotation': [{'hpoId': 'HP:0004631', 'hpoName': 'decreased cervical spine flexion due to contractures of posterior cervical muscles', 'rating': '0.683'}, {'hpoId': 'HP:0032774', 'hpoName': 'focal impaired awareness autonomic seizure with urge to urinate/defecate', 'rating': '0.6818'}, {'hpoId': 'HP:0032779', 'hpoName': 'focal impaired awareness autonomic seizure with pupillary dilation/constriction', 'rating': '0.6818'}, {'hpoId': 'HP:0032805', 'hpoName': 'focal impaired awareness sensory seizure with vestibular features', 'rating': '0.6761'}, {'hpoId': 'HP:0005267', 'hpoName': 'premature delivery because of cervical insufficiency or membrane fragility', 'rating': '0.6753'}]}, 
            {'start': 1888, 'length': 110, 'negated': False, 'concerned_person': 'Pt1', 'mult_CS': False, 'hpoAnnotation': [{'hpoId': 'HP:0003397', 'hpoName': 'generalized hypotonia due to defect at the neuromuscular junction', 'rating': '0.6623'}, {'hpoId': 'HP:0010094', 'hpoName': 'complete duplication of the proximal phalanx of the hallux', 'rating': '0.6598'}, {'hpoId': 'HP:0010422', 'hpoName': 'complete duplication of the proximal phalanx of the 2nd toe', 'rating': '0.6584'}]}, 
            {'start': 1472, 'length': 35, 'negated': False, 'concerned_person': 'Pt1', 'mult_CS': False, 'hpoAnnotation': [{'hpoId': 'HP:0004437', 'hpoName': 'cranial hyperostosis', 'rating': '0.7157'}, {'hpoId': 'HP:0004540', 'hpoName': 'congenital, generalized hypertrichosis', 'rating': '0.7119'}, {'hpoId': 'HP:0008399', 'hpoName': 'circumungual hyperkeratosis', 'rating': '0.7104'}, {'hpoId': 'HP:0005733', 'hpoName': 'spinal stenosis with reduced interpedicular distance', 'rating': '0.708'}, {'hpoId': 'HP:0025351', 'hpoName': 'recurrent interdigital mycosis', 'rating': '0.7075'}]}, 
            {'start': 1560, 'length': 168, 'negated': False, 'concerned_person': 'Pt1', 'mult_CS': False, 'hpoAnnotation': [{'hpoId': 'HP:0007409', 'hpoName': 'obsolete absence of subcutaneous fat over entire body except buttocks, hips, and thighs', 'rating': '0.7253'}, {'hpoId': 'HP:0010270', 'hpoName': 'cone-shaped epiphyses of the proximal phalanges of the hand', 'rating': '0.691'}, {'hpoId': 'HP:0004631', 'hpoName': 'decreased cervical spine flexion due to contractures of posterior cervical muscles', 'rating': '0.6898'}, {'hpoId': 'HP:0020188', 'hpoName': 'anterior predominant pachygyria with 5-10 mm cortical thickness', 'rating': '0.6872'}, {'hpoId': 'HP:0004594', 'hpoName': 'hump-shaped mound of bone in central and posterior portions of vertebral endplate', 'rating': '0.6861'}]}, 
            {'start': 147, 'length': 100, 'negated': False, 'concerned_person': 'Pt1', 'mult_CS': False, 'hpoAnnotation': [{'hpoId': 'HP:0032662', 'hpoName': 'focal-onset seizure evolving into bilateral convulsive status epilepticus', 'rating': '0.662'}, {'hpoId': 'HP:0007480', 'hpoName': 'decreased sweating due to autonomic dysfunction', 'rating': '0.6615'}]}, 
            {'start': 1507, 'length': 53, 'negated': False, 'concerned_person': 'Pt1', 'mult_CS': False, 'hpoAnnotation': [{'hpoId': 'HP:0004631', 'hpoName': 'decreased cervical spine flexion due to contractures of posterior cervical muscles', 'rating': '0.6774'}, {'hpoId': 'HP:0003397', 'hpoName': 'generalized hypotonia due to defect at the neuromuscular junction', 'rating': '0.672'}, {'hpoId': 'HP:0010082', 'hpoName': 'symphalangism affecting the distal phalanx of the hallux', 'rating': '0.6718'}, {'hpoId': 'HP:0010091', 'hpoName': 'symphalangism affecting the proximal phalanx of the hallux', 'rating': '0.6698'}, {'hpoId': 'HP:0007409', 'hpoName': 'obsolete absence of subcutaneous fat over entire body except buttocks, hips, and thighs', 'rating': '0.6694'}]}, 
            {'start': 1181, 'length': 101, 'negated': False, 'concerned_person': 'Pt1', 'mult_CS': False, 'hpoAnnotation': [{'hpoId': 'HP:0007480', 'hpoName': 'decreased sweating due to autonomic dysfunction', 'rating': '0.6826'}, {'hpoId': 'HP:0032852', 'hpoName': 'focal impaired awareness cognitive seizure with conduction dysphasia/aphasia', 'rating': '0.6725'}, {'hpoId': 'HP:0032886', 'hpoName': 'focal impaired awareness cognitive seizure with expressive dysphasia/aphasia', 'rating': '0.6703'}, {'hpoId': 'HP:0032793', 'hpoName': 'focal impaired awareness cognitive seizure with receptive dysphasia/aphasia', 'rating': '0.669'}, {'hpoId': 'HP:0007409', 'hpoName': 'obsolete absence of subcutaneous fat over entire body except buttocks, hips, and thighs', 'rating': '0.6647'}]}, 
            {'start': 852, 'length': 203, 'negated': False, 'concerned_person': 'Pt1', 'mult_CS': False, 'hpoAnnotation': [{'hpoId': 'HP:0002373', 'hpoName': 'febrile seizure (within the age range of 3 months to 6 years)', 'rating': '0.732'}, {'hpoId': 'HP:0032895', 'hpoName': 'febrile seizure outside the age of 3 months to 6 years', 'rating': '0.6896'}, {'hpoId': 'HP:0032774', 'hpoName': 'focal impaired awareness autonomic seizure with urge to urinate/defecate', 'rating': '0.6848'}, {'hpoId': 'HP:0032788', 'hpoName': 'focal impaired awareness autonomic seizure with palpitations/tachycardia/bradycardia/asystole', 'rating': '0.6764'}, {'hpoId': 'HP:0004631', 'hpoName': 'decreased cervical spine flexion due to contractures of posterior cervical muscles', 'rating': '0.6742'}]}]
            annotations_EL=ENLIGHTOR_results_normalization(annotations_EL)
            #annotations_EL=[{'start': 500, 'length': 81, 'negated': False, 'concerned_person': 0, 'mult_CS': False, 'hpoAnnotation': [{'hpoId': 'HP:0001250', 'hpoName': 'Seizure', 'rating': 3},{'hpoId': 'HP:0000717', 'hpoName': 'Autism', 'rating': 3}]},
            # {'start': 853, 'length': 202, 'negated': False, 'concerned_person': 0, 'mult_CS': False, 'hpoAnnotation': [{'hpoId': 'HP:0000612', 'hpoName': 'Iris coloboma', 'rating': 3},{'hpoId': 'HP:0000525', 'hpoName': 'Abnormality iris morphology', 'rating': 3}]}]
            """
    if bParser_StrMatch:
        _,HPO_terms=Extract_HPO_Fr_StringMaching(note)
        HPO_terms=Normalize_Annotation_Format(HPO_terms)
        HPO_terms=HPO_terms[["start","length","negated","concerned_person","mult_CS","HPO_ID","HPO_Terms","score"]]
        annotations_SM=Annotation_DF2List(HPO_terms)
        
    # add the Parser ID (thus we can know later the source of each proposed term)
    for i in range(len(annotations_SM)):
        for j in range(len( annotations_SM[i]['hpoAnnotation'])):
            annotations_SM[i]['hpoAnnotation'][j]['parser']='StrMatch'
    
    for i in range(len(annotations_EL)):
        for j in range(len( annotations_EL[i]['hpoAnnotation'])):
            annotations_EL[i]['hpoAnnotation'][j]['parser']='ENLIGHTOR'

    # concatinate the annotations
    annotations=annotations_SM+annotations_EL

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
    session['note']= note

    return json.dumps(annotations)

# @app.route("/note/parse/bcomSM",methods=['POST','GET'])
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
        concerned_person=request.json['concerned_person']
        start=request.json['start']
        for anno in annotations:
            if anno['start']==start:                
                anno['negated']=negated
                anno['mult_CS']=mult_CS
                anno['concerned_person']=concerned_person
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
        newEntry={'start': start, 'length': length, 'negated': False, 'concerned_person': 0, 'mult_CS': False, 'validated':False,
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
    #    in the merged ranges (without repetition). If there is a conflict between the 'negated', 'MCS' or 'concerned_person' 
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
            concerned_persons=[]
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
                    concerned_persons.append(annotations[rngIndexUnions[i][j]]['concerned_person'])
                
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
            if len(concerned_persons):
                curDict['concerned_person']=max(set(concerned_persons), key=concerned_persons.count)
            else:
                curDict['concerned_person']=-1
            
            # keep only unique IDs in hpoAnnotations
            
            # for now , just filter out the duplicates
            hpoAnnotation=list({v['hpoId']:v for v in hpoAnnotationUnion}.values())
            # compare hpoAnnotation with hpoAnnotationUnion to merge parser IDs
            for dict1 in hpoAnnotation:
                hpoId1=dict1["hpoId"]
                parsers=''
                for dict2 in hpoAnnotationUnion:
                    hpoId2=dict2["hpoId"]
                    if hpoId2==hpoId1:
                        parsers=parsers+dict2["parser"]+";"
                dict1["parser"]=parsers[0:-1]

            print("\n-------\n",hpoAnnotation)
            
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

    newDict={'hpoId': hpoID, 'hpoName': hpoTerm, 'rating': 3, 'ratingInit': 0, 'parser': 'Manual'}

    termExists=False

    # add the indicated term (if does not exist)
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
    # add annotated sentences to the output file
    note=session['note']
    for i in range(len(annotations)):
        annoUnit=annotations[i]
        start=annoUnit["start"]
        end=start+annoUnit["length"]
        annotated_sentence=note[start:end]
        annotations[i]["sentence"]=annotated_sentence


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

@app.route("/note/get_annotator_ID",methods=['GET'])
def get_annotator_ID():
    if not session.get('annotatorId'):
        session['annotatorId']="NA"
    annotatorId= session['annotatorId']
    return json.dumps(annotatorId)

@app.route("/note/get_source_ID",methods=['GET'])
def get_source_ID():
    if not session.get('sourceId'):
        session['sourceId']="NA"
    sourceId= session['sourceId']
    return json.dumps(sourceId)
