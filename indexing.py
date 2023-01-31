import os
import subprocess
import pandas as pd
import lucene
import math
from java.io import *
from org.apache.lucene.util import BytesRefIterator, Version
from org.apache.lucene.analysis.tokenattributes import CharTermAttribute
from org.apache.lucene.analysis.standard import StandardAnalyzer
from org.apache.lucene.analysis.en import EnglishAnalyzer
import org.apache.lucene.document as document
from org.apache.lucene.index import IndexWriter, IndexWriterConfig, IndexOptions, DirectoryReader, Term
from org.apache.lucene.store import SimpleFSDirectory, FSDirectory
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from collections import defaultdict


def process_json_tokenize(path):
    return None

def write_tf_idf(numDocs):
    if os.path.exists("temp/idf.txt"):
        os.remove("temp/idf.txt")
        os.remove("temp/tf.txt")
    max_term_per_line = 5
    count = 0
    with open("temp/idf.txt",'w') as f:
        for term in idf:
            if count < max_term_per_line:
                count += 1
            else:
                count = 0
                f.write("\n")
            f.write(f'{term},{idf[term]}|')
        f.close()

    count = 0
    with open("temp/tf.txt",'w') as f:
        for doc_id in range(numDocs):
            for term, num in tf[id].items():
                if count < max_term_per_line:
                    count += 1
                else:
                    count = 0
                    f.write("\n")
                f.write(f'{doc_id},{term},{num}|')
        f.close()


                
def map_tf(text,doc_id,numDocs):
    tokens = word_tokenize(text)
    for word in tokens:
        tf[doc_id][word] += 1

def map_idf(numDocs):
    for doc_id in range(numDocs):
        for term in tf[doc_id]:
            idf[term] += tf[doc_id][term]
    
    for term in idf:
        idf[term] = math.log(numDocs / idf[term])
    

def text_stemming(text):
    analyzer = EnglishAnalyzer()
    stream = analyzer.tokenStream("",text)
    stream.reset()
    tokens = []
    while stream.incrementToken():
        tokens.append(stream.getAttribute(CharTermAttribute.class_).toString())

    stream.close()
    return " ".join(tokens)

def remove_stopwords(text):
    text_tokens = word_tokenize(text)
    tokens = [word for word in text_tokens if not word in stopwords.words()]

    return " ".join(tokens)

def document_insertion(tweets,id,numDocs):
    doc = document.Document()
    field_type = document.FieldType()
    field_type.setStored(True)
    field_type.setTokenized(True)
    field_type.setIndexOptions(IndexOptions.DOCS_AND_FREQS)
    field_type.setStoreTermVectors(True)

    new_text = text_stemming(tweets['text'])
    new_text = remove_stopwords(new_text)

    # calculate tf 
    map_tf(new_text,id,numDocs)

    id_field = document.Field("id",tweets['id'],field_type)
    text_field = document.Field("processed_text",new_text,field_type)
    original_text_field = document.Field("text",tweets['text'],field_type)
    cor_field = document.Field("coordinates",tweets['coordinates'],field_type)
    name_field = document.Field("user_name",tweets['user_name'],field_type)

    doc.add(text_field) 
    doc.add(id_field)
    doc.add(cor_field) 
    doc.add(name_field)
    doc.add(original_text_field)
    writer.addDocument(doc)
    return doc

if __name__ == "__main__":
    # if not os.path.exists("data/tweets.csv"):
    #     process_json("path to tweets_json")
    # df = pd.read_csv("path to data.csv")

    lucene.initVM()
    if os.path.exists("index/"):
        print('remove index folder\n')
        subprocess.run("rm -r index",shell=True)
    
    # create index object
    indexPath = File("index/").toPath() # create index path
    indexDir = FSDirectory.open(indexPath) # create lucene store object to store index in hard disk
    writerConfig = IndexWriterConfig(StandardAnalyzer()) # create index configuration object. allow us to configure the index
    writer = IndexWriter(indexDir,writerConfig) # create index writer with the input of index path and configuration 

    # read each document and use index writer to write to the index
    tf = defaultdict(lambda: defaultdict(int))
    idf = defaultdict(int)

    df = [{'text':'this is a example text','id':'12345','coordinates':'1:1|2:2','user_name':'jeff'},
          {'text':'Nick likes playing football, he is too strong','id':'124','coordinates':'1:1|2:2','user_name':'tim'},
          {'text':'I have an apple, the man who is doing his works','id':'134','coordinates':'1:1|2:2','user_name':'david'},
    ]

    fields = ['text','id','user_name','coordinates']
    id = 0
    numDocs = len(df)
    for tw in df:
        d = document_insertion(tw,id,numDocs)
        if id < 10:
            print("Document Inserted:")
            print('---------------------------')
            for f in d.getFields():
                print(f'{f.name()}: {f.stringValue()}')
            
            print('---------------------------')
        id += 1

    writer.close()

    # calculate idf for each term
    map_idf(numDocs)
    write_tf_idf(numDocs)