import os
import subprocess
import lucene
import math
import json
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


def getElement(co):
    if len(co) > 0 and isinstance(co[0],list):
        return getElement(co[0])
    else:
        co[0] = float(co[0])
        co[1] = float(co[1])
        return co

def process_json_tokenize(path):
    data = []
    with open("data/sample.json","r") as file:
        tweets = json.load(file)
        for t in tweets:
            tw = {}
            for k,v in t.items():
                if k == 'Coordinates':
                    tw['Coordinates'] = getElement(v)
                elif k == 'Entities':
                    for ek, vk in v.items():
                        if ek == 'hashtags':
                            hashtags = []
                            for tag in vk:
                                hashtags.append(str(tag['text']))
                            tw['hashtags'] = " ".join(hashtags)
                        elif ek == 'media' or ek == 'urls':
                            if len(vk) > 0:
                                for key,value in vk[0].items():
                                    if key == "expanded_url":
                                        tw['url'] = str(value)
                else:
                    tw[k] = str(v)
            data.append(tw)
    return data

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
    tokens = [word for word in text_tokens if not word in stopwords.words('english')]

    return " ".join(tokens)

def format_coordinate(num):
    if num < 0:
        num = f'{abs(num):0>13.4f}'.replace('.','d')
        new_num = ''
        for i in num:
            if i == 'd':
                continue
            new_num += str(9-int(i))
        num = "n" + new_num
    else:
        num = f'{num:0>13.4f}'.replace('.','d')
        num = "p" + num
    print(num)
    return num
    

def document_insertion(tweets,id,numDocs):
    doc = document.Document()

    metaType = document.FieldType()
    metaType.setStored(True)
    metaType.setTokenized(False)

    text_field_type = document.FieldType()
    text_field_type.setStored(False)
    text_field_type.setTokenized(True)
    text_field_type.setIndexOptions(IndexOptions.DOCS_AND_FREQS)

    hashtag_field_type = document.FieldType()
    hashtag_field_type.setStored(True)
    hashtag_field_type.setTokenized(True)
    hashtag_field_type.setIndexOptions(IndexOptions.DOCS)
    
    #new_text = text_stemming(tweets['text'])
    new_text = remove_stopwords(tweets['Text'])

    # calculate tf 
    map_tf(new_text,id,numDocs)
    tweets['processed_text'] = new_text.lower()

    for key in tweets:
        if key == "Tweet_ID":
            doc.add(document.Field(key,tweets[key],metaType))
        elif key == "processed_text":
            doc.add(document.Field(key,tweets[key],text_field_type))
        elif key == "Coordinates":
            doc.add(document.LatLonPoint('Coordinates',tweets[key][1],tweets[key][0]))
        elif key == "hashtags":
            doc.add(document.Field(key,tweets[key],hashtag_field_type))
        elif key != "Text":
            doc.add(document.Field(key,tweets[key].lower(),document.TextField.TYPE_STORED))

    writer.addDocument(doc)
    return doc

if __name__ == "__main__":

    lucene.initVM()
    
    df = process_json_tokenize("data/sample.json")

    if os.path.exists("index/"):
        print('remove index folder\n')
        subprocess.run("rm -r index",shell=True)
    
    # create index object
    indexPath = File("index/").toPath() # create index path
    indexDir = FSDirectory.open(indexPath) # create lucene store object to store index in hard disk
    writerConfig = IndexWriterConfig(StandardAnalyzer()) # create index configuration object. allow us to configure the index
    writerConfig.setOpenMode(IndexWriterConfig.OpenMode.CREATE)
    writer = IndexWriter(indexDir,writerConfig) # create index writer with the input of index path and configuration 

    # read each document and use index writer to write to the index
    tf = defaultdict(lambda: defaultdict(int))
    idf = defaultdict(int)

    id = 0
    numDocs = len(df)
    for tw in df:
        d = document_insertion(tw,id,numDocs)
        if id < 10:
            print("Document Inserted:")
            print('---------------------------')
            for f in d.getFields():
                print(f'{f}')
            
            print('---------------------------')
        id += 1

    writer.close()

    # calculate idf for each term
    map_idf(numDocs)
    write_tf_idf(numDocs)