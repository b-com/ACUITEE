# ParserSM.py – Software ACUITEE
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

import numpy as np
import pandas as pd
import re
import csv
from nltk import ngrams,RegexpTokenizer
from nltk.tokenize.util import regexp_span_tokenize
from application.Global_objects import HPO_TERMS,AC_OBJ

def HPO_ID2Term(HPO_ID): #  works with a list of IDs 
    # if we have one ID, convert it to a list of one item
    if not isinstance(HPO_ID, list): 
        HPO_ID=[HPO_ID]
    # load the hpo terms
    with open ('application/resources/hpoterms08022021.txt', 'r') as f:
        hpo_list = [row for row in csv.reader(f,delimiter='\t')]

    hpo_term=np.array(hpo_list)
    # 
    terms=[]
    for CurId in HPO_ID:
        curTerms=[str(term[0]) for term in hpo_term if term[1]==CurId]
        curTerms=np.unique(curTerms)
        terms.append(curTerms.tolist())
    return terms

def Annotation_PostProcessing(annotations):
    # post processing the output annotations:
    # 1- The HPO dataset contains not only terms describing phenotypic abnormality but also
    #    terms describing: 1- the mode of inheritance, 2- clinical modifiers, 3- clinical 
    #    course, and 4- the frequency with patients that show a particular clinical feature.
    #    Finally, we should keep only "phenotypic abnormality" terms. Removing all other
    #    terms from the beginning (as preprocessing) is not consistent with the proposed
    #    algorithm. Instead, we remove the non-desired terms in a post processing step.
    #    To do so, we use the list of HPO_IDs that correspond to "phenotypic abnormality".
    #    This list is stored in a file named HPO_PhAb_IDs.npy (in the resources).
    #    This file is generated using the script: Generate_HPO_PhAb_IDs.py. Note that,
    #    for compatibility, this list is extracted from the adopted frozen version of the
    #    HPO dataset (08/02/2021).
    #    Instead, we can use the complementary set HPO_Non_PhAb_IDs (more efficient since
    #    we have much less terms that dont belonge to the phenotypic abnormality parent).
    # 2- if the annotated phrase contains a comma or a point, remove it.
    #    It belongs to two sentences.
    # 3- treat the overlapped annotated spans. To take into account: the score of the extracted 
    #    term and the length of the annotated phrase (preference for longer phrases).
    # 4- Keep only the terms with highest score (one term per annotated phrase).
    #    Anyway, we save all the resultant dataframes.
    # 5- orgainze the annotations dataframe in the same format of the manual annotation tables.
    #______________________________________________________________________________
    
    print('Post processing')

    # 1- From the results (annotation dataframe) remove terms that does NOt represent 
    #    phenotypic abnormality.
    
    HPO_Non_PhAb_IDs=np.load('application/resources/HPO_Non_PhAb_IDs.npy',allow_pickle=True)
    annotations_PhAb=annotations[~annotations['HPO_ID'].isin(HPO_Non_PhAb_IDs)]
    #______________________________________________________________________________
    
    # 2- if the annotated phrase contains a comma or a point, remove it.
    annotations_PhAb=annotations_PhAb.where(annotations_PhAb['phrase'].str.find(",")==-1)
    annotations_PhAb=annotations_PhAb.dropna()
    annotations_PhAb=annotations_PhAb.where(annotations_PhAb['phrase'].str.find(".")==-1)
    annotations_PhAb=annotations_PhAb.dropna()
    #______________________________________________________________________________
    
    # 3- treat the overlapped annotated spans
    # first, sort the annotations dataframe according to the start field. New indices are assigned {0,1,...,n-1}.
    annotations_PhAb=annotations_PhAb.sort_values(by=['start'],ignore_index=True)
    # insert a new colomn : group_ID . To be used to group up the ovelapped spans
    annotations_PhAb.insert(5, "group_ID", np.zeros(len(annotations_PhAb))-1, True) 
    # loop over the annotations and assign the group numbers
    group_ID=-1
    prevStart=-1
    prevLength=0
    
    for index, row in annotations_PhAb.iterrows():
        curStart=row['start']
        curLength=row['length']
        prevEnd=prevStart+prevLength
        if curStart<prevEnd: # there is an overlap
            prevLength=curLength+prevLength-(prevEnd-curStart) # we keep the first start (in the group). 
        else: # new group
            group_ID+=1
            prevStart=curStart
            prevLength=curLength
        
        annotations_PhAb.at[index,'group_ID']=group_ID
     
    # create an empty dataframe to store the postprocessed annotations       
    empty_annotation_frame = pd.DataFrame(columns = ["start","length","phrase","HPO_ID","score","group_ID"])
    annotations_final = empty_annotation_frame
    # loop over groups to filter the terms inside each group
    for i in range(group_ID+1):
        curGroup=annotations_PhAb[annotations_PhAb['group_ID']==i]    
        if len(curGroup)==1:
            annotations_final=annotations_final.append(curGroup,ignore_index=True) 
        else:
            curGroup=curGroup.sort_values(by=['score'],ignore_index=True,ascending=False)        
            filteredGroup=empty_annotation_frame
            hpoIDs=np.unique(curGroup['HPO_ID']).astype(str)
            for j in hpoIDs:
                tempGroup=curGroup[curGroup['HPO_ID']==j]
                tempGroup.reset_index(inplace=True,drop=True)
                bestRow=tempGroup.loc[np.argmax(tempGroup['score'])]
                filteredGroup=filteredGroup.append(bestRow,ignore_index=True) 
            
            # all terms in one group should have the same : start, length and phrase
            # we select them from the highest score row
            # in case the highest score belongs to several terms (this could take place especially when
            # the highest score=0), we prefer the longest one.
            filteredGroup=filteredGroup.sort_values(by=['length'],ignore_index=True,ascending=False)
            bestRow=filteredGroup.loc[np.argmax(filteredGroup['score'])] # with numpy argmax, only the first occurrence is returned
            start=bestRow['start']
            length=bestRow['length']
            phrase=bestRow['phrase']
            for index, row in filteredGroup.iterrows():
                filteredGroup.at[index,'start']=start
                filteredGroup.at[index,'length']=length
                filteredGroup.at[index,'phrase']=phrase
            
            # sort the filtered group according to the score
            filteredGroup=filteredGroup.sort_values(by=['score'],ignore_index=True,ascending=False)
            
            annotations_final=annotations_final.append(filteredGroup,ignore_index=True) 
            
    #______________________________________________________________________________  
    # add a colomn to the final annotations containing the list of terms that correspond to the extracted IDs
    final_IDs=annotations_final['HPO_ID'].tolist()
    final_terms=HPO_ID2Term(final_IDs)
    
    annotations_final['HPO_Terms']=final_terms
    #______________________________________________________________________________     
    # 4- Keep only the terms with highest score.
    # annotations_final is sorted with respect to 'start' and the terms inside each group
    # are sorted with respect to the score.
    # we simply keep the first term in each group
    empty_annotation_frame = pd.DataFrame(columns = ["start","length","phrase","HPO_ID","score","HPO_Terms"])
    annotations_final_compact = empty_annotation_frame
    group_IDs=np.unique(annotations_final['group_ID'])
    # loop over groups to filter the terms inside each group
    """for i in group_IDs:
        curGroup=annotations_final[annotations_final['group_ID']==i]
        curGroup=curGroup.reset_index()
        #curGroup.at[0,'HPO_ID']=[curGroup.loc[0]['HPO_ID']]
        curGroup.at[0,'HPO_ID']=[curGroup.loc[j]['HPO_ID'] for j in range(len(curGroup)) if curGroup.loc[j]['score']==curGroup.loc[0]['score']]
        curGroup.at[0,'HPO_Terms']=[curGroup.loc[j]['HPO_Terms'] for j in range(len(curGroup)) if curGroup.loc[j]['score']==curGroup.loc[0]['score']]
        curGroup.at[0,'score']=[curGroup.loc[j]['score'] for j in range(len(curGroup)) if curGroup.loc[j]['score']==curGroup.loc[0]['score']]
        annotations_final_compact=annotations_final_compact.append(curGroup.loc[0],ignore_index=True)"""

    for i in group_IDs:
        curGroup=annotations_final[annotations_final['group_ID']==i]
        curGroup=curGroup.reset_index()
        #curGroup.at[0,'HPO_ID']=[curGroup.loc[0]['HPO_ID']]
        best_Index=0
        biggestLength=0
        for j in range(len(curGroup)):
            if curGroup.loc[j]['score']==curGroup.loc[0]['score']:
                if curGroup.loc[j]['length']>biggestLength:
                    biggestLength=curGroup.loc[j]['length']
                    best_Index=j        
        # convert into lists (for compatibility)
        curGroup.at[best_Index,'HPO_ID']=[curGroup.loc[best_Index]['HPO_ID']]
        curGroup.at[best_Index,'HPO_Terms']=[curGroup.loc[best_Index]['HPO_Terms']]
        curGroup.at[best_Index,'score']=[curGroup.loc[best_Index]['score']]
        annotations_final_compact=annotations_final_compact.append(curGroup.loc[best_Index],ignore_index=True)
    
        
    #______________________________________________________________________________ 
    # 5-orgainze the annotations dataframe in the same format of the manual annotation tables
    empty_annotation_frame = pd.DataFrame(columns = ["start","length","phrase","HPO_ID","score","HPO_Terms"])
    annotations_regrouped = empty_annotation_frame
    group_IDs=np.unique(annotations_final['group_ID'])
    # loop over groups to filter the terms inside each group
    for i in group_IDs:
        curGroup=annotations_final[annotations_final['group_ID']==i]
        curGroup=curGroup.reset_index()
        curGroup.at[0,'HPO_ID']=[hpoId for hpoId in curGroup['HPO_ID']]
        curGroup.at[0,'score']=[score for score in curGroup['score']]
        curGroup.at[0,'HPO_Terms']=[terms for terms in curGroup['HPO_Terms']]
        annotations_regrouped=annotations_regrouped.append(curGroup.loc[0],ignore_index=True)
        
    annotations_regrouped=annotations_regrouped[["start","length","phrase","HPO_ID","HPO_Terms","score"]]
    annotations_final_compact=annotations_final_compact[["start","length","phrase","HPO_ID","HPO_Terms","score"]]
        
    return annotations_final_compact,annotations_regrouped

def Ascendant_str2num(AscStr):
    predef_pat={'Pt1':0,'Pt2':1,'Mat':2,'Par':3,'Oth':4}
    return predef_pat[AscStr]

def Annotation_DF2List(annotations_df):
    # convert the annotations dataframe to a list in order to be jsonified in the expected way
    # i.e. a  json structure compatible with the manual annotator
    annotations_list=[]
    for index, row in annotations_df.iterrows():
        curIDlist=row['HPO_ID'] # list of strings
        curTermslist=row['HPO_Terms'] # list of lists
        curScoreList=row['score'] # list of int
        
        curHpoTermsDictList=[] # list of dictionaries
        for i in range(len(curIDlist)):
            curDict={"hpoId":curIDlist[i],"hpoName":curTermslist[i][0],"rating":curScoreList[i]}
            curHpoTermsDictList.append(curDict)
       
        curAnnotationDict={
                 "start":row['start'],
                 "length":row['length'],
                 "negated":row['negated'],
                 "ascendant":Ascendant_str2num(row['patient']),
                 "mult_CS":row['mult_CS'],
                 "hpoAnnotation":curHpoTermsDictList
                }
        annotations_list.append(curAnnotationDict)
    return annotations_list

def Normalize_Annotation_Format(df):
    # All annotation dataframes should follow this format:
    # Header: ["start","length","phrase","HPO_ID"	,"HPO_Terms","score","negated","patient"]
    # where:
    # 1- start is an integer. It represents where the annotated phrase starts (number of characters from the beginning of the text)
    # 2- length is an integer. It represents the length of the annotated phrase (number of characters).
    # 3- phrase is a string. It represents the annotated phrase.
    # 4- HPO_ID is a list of strings. It represents the HPO IDs selcetd for annotating the corresponding phrase.
    # 5- HPO_Terms is a list of strings. It represents the HPO Terms that correspond to the HPO IDs.
    # 6- score is a list of integers between 0 and 1. It represnts the scores given for each selected HPO term.
    # 7- negated is a boolean variable. It represents the negation status.
    # 8- patient is a string: Pt1 for patient number 1, Pt2 for patient number 2, Par for Parental line, Mat for 
    # maternal line and Oth for other cases.
    # ------------------------------------------
    
    # check if the df contains 'negated' field. If not 
    # we add the default (negated=false)
    if 'negated' not in df.columns:
        negated_default=[False]*len(df)
        df['negated']=negated_default
    df['negated']=df['negated'].astype(bool)   
    # check if the df contains 'patient' field. If not 
    # we add the default (patient='Pt1')
    if 'patient' not in df.columns:
        patient_default=['Pt1']*len(df)
        df['patient']=patient_default        
    else:# for compatibility with old versions, convert True to Pt1 and False to Oth
        predef_pat=['Pt1','Pt2','Mat','Par','Oth']
        if df['patient'][0] not in predef_pat:
            df['patient']=df['patient'].replace(True,'Pt1')
            df['patient']=df['patient'].replace(False,'Oth')
            df['patient']=df['patient'].replace('cas index','Pa1')
            
       
    # check if the df contains 'score' field. If not,
    # we add the default score =3
    if 'score' not in df.columns:
        score_default=[[3]*len(curID) for curID in  df['HPO_ID']]
        df['score']=score_default
    else: # project the score from the range [0,1] to the set {0,1,2,3}
        score_projected=[[round(x * 3) for x in curScores]  for curScores in df['score']]
        df['score']=score_projected
        
    if 'mult_CS' not in df.columns:
        mcs_default=[False]*len(df)
        df['mult_CS']=mcs_default    
 
    # put the columns of the annotations_auto in the same order as annotations_manual (for automating the comparison)
    df=df[["start","length","phrase","HPO_ID","HPO_Terms","score","negated","patient","mult_CS"]]
    return df

# define the tokenization funtion 
def tokenize_fr(text_in):
    # output=word_tokenize(text_in.lower(),language='french')
    toknizer_fr = RegexpTokenizer(r'''\w'|\w+|[^\w\s]''') # word tokenizer for french sentences
    output=toknizer_fr.tokenize(text_in.lower())
    return output

def Extract_HPO_Fr_StringMaching(note_med):
    # put the medical note in lower case
    note_original = note_med.lower()
    
    # find the matches in the medical note
    res_ind=AC_OBJ.find_matches_as_indexes(note_original,overlapping=True)
    
    # extract the corresponding hpo terms
    res_hpo_terms=np.array([HPO_TERMS[res_ind[i][0]] for i in range(len(res_ind))])
    
    # post processing
    # split the medical note and retrieve the corresponding spans
    note_spans=list(regexp_span_tokenize(note_original, r'\W+'))
    
    indices_q=[m.start() for m in re.finditer("'" ,note_original)] # indices of the charachter "'"
    note_spans=[(span[0],span[1]+1) if span[1] in indices_q else span for span in note_spans] # to consider "'" in the spans
    note_splt=[note_original[span[0]:span[1]].lower() for span in note_spans]
    
    # Split the sentences in the target HPO terms and retrieve 
    # the corresponding sentence' sizes (number of words in each sentence)
    hpo_splt=[tokenize_fr(x) for x in res_hpo_terms[:,0]]
    hp_seg_len=np.array([len(x) for x in hpo_splt])
    thresh_ngrams=max(hp_seg_len)
    #______________________________________________________________________________
    
    # create (an empty) dataframe for the storing the annotations
    annotations = pd.DataFrame(columns = ["start","length","phrase","HPO_ID","score"])
    #______________________________________________________________________________
                        
    # keep only the matches that represent a set of full tokens
    for i in range(1,thresh_ngrams+1):
        igrams = list(ngrams(note_splt, i))
        for j in range(len(igrams)):
            note_grams=igrams[j]
            for k in range(len(hpo_splt)):
                hpo_grams=hpo_splt[k]
                if tuple(hpo_grams)==note_grams:
                    start=note_spans[j][0]
                    length=note_spans[j+i-1][1]-start
                    curPhrase=note_original[start:start+length]
                    #new_row={'start':start,'length':length,'phrase':curPhrase,'HPO_ID':hpo_ID_short[k],'score':1}
                    new_row={'start':start,'length':length,'phrase':curPhrase,'HPO_ID':res_hpo_terms[k,1],'score':1}
                    
                    annotations=annotations.append(new_row,ignore_index=True)
                    print(f'start: {start:4} | length: {length:2} | {curPhrase}')
    
    annotations_final_compact,annotations_final=Annotation_PostProcessing(annotations)
    return annotations_final_compact,annotations_final