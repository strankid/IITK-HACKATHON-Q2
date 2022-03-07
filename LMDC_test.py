# Team BruteForce/ Team apoorv365_c3cd submission for problem 2 LMDC_test
import numpy as np
import pandas as pd 
import pickle
import os, sys
import base64
from os import listdir
from os.path import isfile, join
import binascii
from elftools.elf.elffile import ELFFile, ELFError
from pprint import pprint
from collections import Counter
import random
from pickle import load
import xgboost as xgb
import copy 

random.seed(a=1234567)


# read a file and parse the text section of elf file into a string
# returns empty string when there is no text section, or file is not a valid elf file
def process_file(Binaries_list, filename, file_sections = ['.text', '.comment']):
    out_array = []
    with open(filename, 'rb') as f:
        try:
            elffile = ELFFile(f)
            section_list = {}
            for section in elffile.iter_sections():
                section_list[section.name] = section.data()
            
            for file_section in file_sections:
                try:
                    fbuf = section_list[file_section]
                    out_array.append(fbuf.hex())
                except:
                    out_array.append('')
            
            Binaries_list.append(out_array)  
            return ''
        except ELFError:
            print("Error opening file")
            return 'NOTELF'
# Structures for Data extraction
Binaries_list = [] #possible change to df
distinct_labels = []
num_duplicates = 0

extract_sections = [".text", ".strtab" ,".rodata",".comment",".note", ".symtab",'.init'] 
distinct_labels= ['Backdoor', 'Botnet', 'DDoS', 'Trojan', 'Virus', 'Benign']

def main(argv):
    if len(argv) != 1:
        print("Please enter a valid path while calling IDS_test.py in the command line")
        return
    print(argv[0])
    input_dir_path=argv[0]
    
    # load all benign files names
    input_file_names = [input_dir_path + f for f in listdir(input_dir_path) if isfile(join(input_dir_path, f))]
   
    not_elf_files=[]
    # make byte level array for text section of each file
    for i, file_name in enumerate(input_file_names):
        print("path: ", file_name)
        rc = process_file(Binaries_list,file_name, extract_sections)
        if rc=='NOTELF':
            not_elf_files.append(i)
            
    print(not_elf_files)
    
    Binaries_df = pd.DataFrame(Binaries_list)

    print('binaries length: ', len(Binaries_list))
  
    from sklearn.feature_extraction.text import TfidfVectorizer

    max_features = 75   
    df_test=   pd.DataFrame(index=np.arange(Binaries_df.shape[0]),columns=np.arange(max_features*Binaries_df.shape[1] )) 
    cumulator= 0
    
      


    for i in range(Binaries_df.shape[1]):
        vectorizer_3 = load(open('trans-'+extract_sections[i]+'.pkl', 'rb'))
    
        #fit TF-IDF model using testing data and transform testing data according to the fitted model 
        X_test = vectorizer_3.transform(Binaries_df[i])
        No_Columns = pd.DataFrame(X_test.toarray()).shape[1]
        df_test.iloc[: , cumulator:cumulator + No_Columns] = pd.DataFrame(X_test.toarray())

        cumulator += No_Columns

      

    df_test.drop(df_test.columns.to_series()[cumulator:], axis=1, inplace=True)
    XGB_model = xgb.XGBClassifier(objective="multi:softprob", random_state=1234567, use_label_encoder=False, n_estimators = 100)
    XGB_model.load_model("XGB_model")
    class_out = XGB_model.predict(df_test.values)
    final_df = pd.DataFrame(columns=['FILENAME','CLASS'])
    


    df_i = 0
    for i, file in enumerate(input_file_names):
        if i in not_elf_files:
            a_series = pd.Series([file, 'NOTELF'], index = final_df.columns)
            final_df = final_df. append(a_series, ignore_index=True)
        else:
            a_series = pd.Series([file, distinct_labels[class_out[df_i]]], index = final_df.columns)
            final_df = final_df.append(a_series, ignore_index=True)
            df_i = df_i + 1 
                    
    final_df.to_csv('result.csv',index=False)
    
    
    
    
    

    





       
         

        
    
    
    

    
if __name__ == "__main__":
    main(sys.argv[1:])