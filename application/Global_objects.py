# Global_objects.py – Software ACUITEE
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

from os import path
import csv
import numpy as np
from pronto import Ontology
import ahocorasick_rs


def Load_HPO_Local_Preprocessed():
    # Load the local version of the HPO dataset (preprocessed version with only terms that represent phynotypic abnormality)
    # Assumption: we use the frozen version of the HPO dataset 08-02-2021
    hpo_file_name= "hpoterms08022021_en_fr.txt"
    preprocessed_file_name='application/resources/HPO_preprocessed.npy'
    
    if path.exists(preprocessed_file_name):
        hpo_array=np.load(preprocessed_file_name)
    else:        
        with open ('application/resources/'+hpo_file_name, 'r',encoding="utf-8") as f:
            #hpo_list = [row for row in csv.reader(f,delimiter='\t')]
            hpo_list = [[row[0].lower(),row[1]] for row in csv.reader(f,delimiter='\t')]
        
        hpo_array=np.array(hpo_list)
        
        # remove the terms whoes IDs are not in the adopted English version of the HPO
        
        hpo_file_name= "hpoterms08022021.txt" # load the english hpo file
                
        with open ('application/resources/'+hpo_file_name, 'r',encoding="utf-8") as f:
            hpo_list_en = [row for row in csv.reader(f,delimiter='\t')]
        
        hpo_term_en=np.array(hpo_list_en)
        HPO_IDs_En=np.unique(hpo_term_en[:,1])
        HPO_IDs_En_Fr_All=hpo_array[:,1]
        HPO_IDs_En_Fr=np.unique(HPO_IDs_En_Fr_All)
        HPO_IDs_2remove=np.array(list(set(HPO_IDs_En_Fr)-set(HPO_IDs_En)))
        
        indices_2keep=[term not in HPO_IDs_2remove for term in HPO_IDs_En_Fr_All]
        hpo_array=hpo_array[indices_2keep]
        
        # remove terms that does NOt represent phenotypic abnormality.
    
        HPO_Non_PhAb_IDs=np.load('application/resources/HPO_Non_PhAb_IDs.npy',allow_pickle=True)
        HPO_IDs=hpo_array[:,1]
        indices_2keep=[term not in HPO_Non_PhAb_IDs for term in HPO_IDs]
        hpo_array=hpo_array[indices_2keep]
        
        # remove repetitions
        _, indices=np.unique(hpo_array[:,0], return_index=True)
        hpo_array=hpo_array[indices]
        
        # save the results 
        np.save(preprocessed_file_name,hpo_array)
        
    return hpo_array

# load the preprocessed hpo terms
HPO_TERMS=Load_HPO_Local_Preprocessed()

# load the hpo obo file
HPO_OBO=Ontology("application/resources/hp08022021.obo")

# Construct an AhoCorasick object
AC_OBJ = ahocorasick_rs.AhoCorasick((HPO_TERMS[:,0]).astype('str'))