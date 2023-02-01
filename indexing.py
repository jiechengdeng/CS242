import os
import subprocess
import lucene
import math
from java.io import *
from org.apache.lucene.analysis.tokenattributes import CharTermAttribute
from org.apache.lucene.analysis.standard import StandardAnalyzer
from org.apache.lucene.analysis.en import EnglishAnalyzer
import org.apache.lucene.document as document
from org.apache.lucene.index import IndexWriter, IndexWriterConfig, IndexOptions
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
    text_field_type = document.FieldType()
    text_field_type.setStored(True)
    text_field_type.setTokenized(True)
    text_field_type.setIndexOptions(IndexOptions.DOCS_AND_FREQS)
    

    new_text = text_stemming(tweets['text'])
    new_text = remove_stopwords(new_text)

    # calculate tf 
    map_tf(new_text,id,numDocs)
    tweets['processed_text'] = new_text

    for key in tweets:
        if key == "Tweet_ID":
            doc.add(document.Field(key,tweets[key]))
        elif key == "text" or key == "processed_text":
            doc.add(document.Field(key,tweets[key],text_field_type))
        elif key == "latitude" or key == "longitude":
            doc.add(document.DoublePoint(key,tweets[key]))
            doc.add(document.Field(key,str(tweets[key]),document.TextField.TYPE_STORED))
        else:
            doc.add(document.Field(key,tweets[key],document.TextField.TYPE_STORED))

    writer.addDocument(doc)
    return doc

if __name__ == "__main__":
    """
    TODO:
    parse the json and create dictionary object for each tweets and append it to a list
    Each tweet should have the following fields:
    1. Tweet_ID
    2. User (Name)
    3. Text
    4. City
    5. Country
    6. Coordinates (store as latitude, longitude)
    7. Hashtags
    8. tweet_url (pick expanded_url field)
    9. Date
    """
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

    df = [{'text':'this is a example text','id':'12345','latitude':123.5,'longitude':456.23,'user_name':'jeff'},
          {'text':'Nick likes playing football, he is too strong','id':'33333','latitude':333.5,'longitude':555.33,'user_name':'tim'},
          {'text':'I have an apple, the man who is doing his works','id':'828282','latitude':999.9,'longitude':666.88,'user_name':'david'},
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