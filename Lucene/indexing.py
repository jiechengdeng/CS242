import os
import pandas as pd
import lucene
from java.io import *
from org.apache.lucene.analysis.tokenattributes import CharTermAttribute
from org.apache.lucene.analysis.standard import StandardAnalyzer
from org.apache.lucene.analysis.en import EnglishAnalyzer
from org.apache.lucene.analysis.core import WhitespaceAnalyzer, SimpleAnalyzer, StopAnalyzer
import org.apache.lucene.document as document
from org.apache.lucene.index import IndexWriter, IndexWriterConfig
from org.apache.lucene.store import SimpleFSDirectory, FSDirectory

def process_json(path):
    return None

def make_inverted_index(path):
    return None
    
def document_insertion():
    return None
if __name__ == "__main__":
    if not os.path.exists("data/tweets.csv"):
        process_json("path to tweets_json")
    
    lucene.initVM()
    df = pd.read_csv("path to data.csv")

    # create index object

    