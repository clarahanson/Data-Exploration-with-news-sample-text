
# coding: utf-8

# In[ ]:


# Before cleaning the data, it must be in .txt format instead of .RTF

# Step 1: Open terminal

# Step 2: type: textutil -convert txt /Users/Clara/Documents/27\ -\ PhD\ 3\ Summer/Research/Data/txt_Data/*.RTF

# Step 3: This code creates a txt copy of every RTF file in the specified folder. Delete excess files. Retreived from http://osxdaily.com/2014/02/20/batch-convert-docx-to-txt-mac/


# In[17]:


# First, I define a function to extract text data, clean it,
# and call the nlp_dictionary function to further process the text
# This code works with documents individually

from __future__ import division

def clean_data (x, y):
    # function takes two arguments where x is a filepath to a text document that should be cleaned,
    # and y is a filepath to where the transformed .json object should be saved
    
    # imports relevant modules 
    import re, os, json
    from datetime import datetime
    
    # opens the file defined by x, imports the text
    test_file = open(x, "r")
    raw_text = test_file.readlines()
    test_file.close()
    
    # extracts the relevant lines from the file, creates a list of strings using regex & ist comprehension 
    pieces_of_data = re.compile('\d+\.\t|\.\.\.[ ]|Date\:')
    news_data = [x for x in raw_text if pieces_of_data.match(x)]
    
    # sets definitions to be used in the cleaning loop
    headline_text = re.compile('\d+\.\\t(.+)\\n')
    date_text = re.compile('Date\: (\d\d\d\d-\d\d-\d\d)\n')
    news_text = re.compile('\.\.\. (.+)[ ]?\.\.[\.+]')
    match = re.match
    dictionary_data = []
    index_ = 1
    
    # cleaning loop
    # follow the logic of the data structure
    # first looks for lines that match headline_text
    # iterates over the following lines to create a set of the news text (which can be of length 1-7)
    # stores the next line that is not news text as a date string
    # returns a list object full of dictionaries that store data about each article
    
    for item in news_data:
        if headline_text.match(item):
            clean_headline = headline_text.match(item)
            temp_dic = {'headline': clean_headline.group(1).lower()}
            temp_text = set()
            while news_text.match(news_data[index_]):
                clean_text = news_text.match(news_data[index_])
                temp_text.add(clean_text.group(1).lower())
                index_+=1
            if not news_text.match(news_data[index_]):
                temp_dic['text']=list(temp_text)
                clean_date = date_text.match(news_data[index_])
                temp_dic['date']=clean_date.group(1)
                index_+=2
                dictionary_data.append(temp_dic)
        if not headline_text.match(item): pass
    
    dictionary_data = nlp_dictionary(dictionary_data, y)
    #the y argument is passed to the NLP dictionary function, where it is used to save the document


# In[18]:


def nlp_dictionary (input_dict, y):

    # This function tokenizes, removes stopwords, and lemmatizes the data
    # It is called within the clean_data function
    # But is written separately so it can be removed should I want to save non-NLP-processed data
    
    import os, re, json, sys, nltk, string
    import pandas as pd
    from nltk.corpus import stopwords
    from nltk import word_tokenize
    from nltk.stem import WordNetLemmatizer
    
    # uses pandas dataframe to remove duplicates - removed for now - deletes many entries with "no headline"
    # and cannot use 'text' as subset bc 'text' is list
    #this step also takes a few seconds to run 
    
    #raw_df = pd.DataFrame(input_dict)
    #deduped_df = raw_df.drop_duplicates(subset='headline', keep='last')
    #raw_data = deduped_df.to_dict('records')
    
    # tokenizing the text - this step is the most time consuming 
    for entry in input_dict:
        entry['headline']=nltk.word_tokenize(entry['headline'])
        tokenized_texts = []
        for each in entry['text']:
            tokenized_texts.append(nltk.word_tokenize(each))
        entry['text']=tokenized_texts
        
    # removing stopwords - also time consuming 
    # note: numbers are still present in text. If I want to remove numbers, add to previous cleaning code 
    stop = stopwords.words('english') + list(string.punctuation) + ['``', "'s", "n't", '--', "''", r'//']
    for entry in input_dict:
        good_headlines = []
        good_texts = []
        for i in entry['headline']:
            if i not in stop:
                good_headlines.append(i)
            else: pass
            entry['headline']=good_headlines
        for each in entry['text']:
            a = []
            for i in each:
                if i not in stop:
                    a.append(i)
                else: pass
            good_texts.append(a)
        entry['text']=good_texts
        
    # lemmatizes the words using wordnet, 
    # pretty conservative in word transformation; use "in context" option in later iterations 
    lemmatizer=WordNetLemmatizer()
    for entry in input_dict:
        lemmed_headline = []
        lemmed_texts = []
        for i in entry['headline']:
            q = str(lemmatizer.lemmatize(i))
            lemmed_headline.append(q)
        entry['headline']=lemmed_headline
        for each in entry['text']:
            a = []
            for i in each:
                q = str(lemmatizer.lemmatize(i))
                a.append(q)
            lemmed_texts.append(a)
        entry['text']=lemmed_texts
        
# saves the dictionary to a JSON object with the name and filepath as the y argument
    with open (y, 'w') as json_document:
        json.dump(input_dict, json_document)    


# In[19]:


# This function iterates over all files in a directory 
# to implement the clean_data function over each file

def clean_directory(input_directory, output_directory):
    # both arguments must be directory names ~~~that end in a forward slash~~~
    import os, glob, re

    # below, I use glob to load a list of directory strings to each text file in the text folder
    # note that glob.glob stores each directory in a list, while glob.iglob is in iterator not used here
    # glob.glob may take up too much memory when used on very large directories 

    text_directory = os.path.join(input_directory, '*.txt')
    file_list = glob.glob(text_directory)
    
    for file in file_list:
        # uses regular expressions to extract unique names from each document in file_list
        extract_name = re.compile(input_directory+'(.+)\.txt')
        unique_name = extract_name.match(file)
        
        # defines x and y variables so each file can be called and saved uniquely using the clean_data function
        x = file
        y = output_directory+unique_name.group(1)+".json"
    
        # calls the clean_data function for each file in file_list, thus cleaning each file & saving it as a .json object
        clean_data (x, y)


# In[20]:


input_directory = "/Users/Clara/Documents/27 - PhD 3 Summer/Research/Data/LN Headline Corpus/txt_Data/"
output_directory = "/Users/Clara/Documents/27 - PhD 3 Summer/Research/Data/LN Headline Corpus/JSON_Data/"

clean_directory(input_directory, output_directory)

