import os
import pandas as pd
import lucene
from java.io import *
from org.apache.lucene import util
from org.apache.lucene.analysis.tokenattributes import CharTermAttribute
from org.apache.lucene.analysis.standard import StandardAnalyzer
from org.apache.lucene.analysis.en import EnglishAnalyzer
from org.apache.lucene.analysis.core import WhitespaceAnalyzer, SimpleAnalyzer, StopAnalyzer
import org.apache.lucene.document as document
from org.apache.lucene.index import IndexWriter, IndexWriterConfig
from org.apache.lucene.store import SimpleFSDirectory, FSDirectory

def process_json_tokenize(path):
    return None

def make_inverted_index(path):
    return None
    
def document_insertion(tweets):
    doc = document.Document()
    
    doc.add(document.Field('text',tweets.text,document.TextField.TYPE_STORED)) 
    doc.add(document.Field('id',tweets.id,document.TextField.TYPE_STORED))
    doc.add(document.Field('coordinates',tweets.coordinate,document.TextField.TYPE_STORED)) 
    doc.add(document.Field('user_name',tweets.username,document.TextField.TYPE_STORED))
    
    writer.addDocument(doc)
    
"""
TF-IDF values should be calculated BEFORE the insertion

calculate TF values: Count the number of occurrences of each term in each document

calculate IDF values: Calculate the logarithmically-scaled inverse fraction of the documents that contain each term

"""
# 有一个list of document，需要计算tfidf分数，
def ranking(documents): 
    # tokennize the documents
    tokenized_docs = [doc.lower().split() for doc in documents]
    
    # calculate the term frequency
    tf = defaultdict(lambda: defaultdict(int))
    for i, doc in enumerate(tokenized_docs):
        for term in doc:
            tf[i][term] += 1
            
    # calculate the inverse document frequency
    idf = defaultdict(int)
    num_docs = len(tokenized_docs)
    for doc in tokenized_docs:
        for term in set(doc):
            idf[term] += 1

    for term in idf.keys():
        idf[term] = math.log(num_docs / idf[term])
        
    # calculate TF-IDF scores
    tfidf = defaultdict(lambda: defaultdict(float))
    for i, doc in enumerate(tokenized_docs):
        for term in doc:
            tfidf[i][term] = tf[i][term] * idf[term]
    
    # Rank the documents
    scores = []
    for i, doc in enumerate(tokenized_docs):
        score = sum(tfidf[i][term] for term in doc)
        scores.append((i, score))

    scores.sort(key=lambda x: x[1], reverse=True)
    
    return [documents[i] for i, _ in scores]  

    



if __name__ == "__main__":
    if not os.path.exists("data/tweets.csv"):
        process_json("path to tweets_json")
    
    lucene.initVM()
    df = pd.read_csv("path to data.csv")

    # create index object
    indexPath = File("index/").toPath() # create index path
    indexDir = FSDirectory.open(indexPath) # create lucene store object to store index in hard disk
    writerConfig = IndexWriterConfig(util.Version.LUCENE_CURRENT,StandardAnalyzer()) # create index configuration object. allow us to configure the index
    writer = IndexWriter(indexDir,writerConfig) # create index writer with the input of index path and configuration 

    # read each document and use index writer to write to the index

    writer.close()

    # search the index
    
