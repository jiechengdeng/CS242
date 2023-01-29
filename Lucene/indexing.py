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
    