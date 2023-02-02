import lucene
import time
import re
from datetime import timedelta
from java.io import *
from org.apache.lucene.search import IndexSearcher, BooleanQuery, BooleanClause
from org.apache.lucene.store import SimpleFSDirectory, FSDirectory
from org.apache.lucene.queryparser.classic import QueryParser, MultiFieldQueryParser
from org.apache.lucene.document import LatLonPoint
from org.apache.lucene.analysis.standard import StandardAnalyzer
from org.apache.lucene.index import DirectoryReader, Term
from indexing import remove_stopwords, format_coordinate
from collections import defaultdict


def end_execution():
    end = time.time()
    print("time elapsed:",str(timedelta(seconds=end-start)))

def extract_numbers(query):
    numbers = re.findall(r"[-+]?\d*\.\d+|\d+",query)
    integers = []
    floats = []
    for i in numbers:
        if '.' in i:
            floats.append(i)
        else:
            integers.append(i)
    return floats, integers

def create_query(query):
    bQ = BooleanQuery.Builder()
    fields = ['processed_text','User','City','Country','hashtags','url']
    occurs = [BooleanClause.Occur.SHOULD for i in range(len(fields))]

    mutliField_parser = MultiFieldQueryParser(fields,analyzer)
    q1 = mutliField_parser.parse(input_query,fields,occurs,analyzer)
    #q1 = QueryParser('processed_text',analyzer).parse(query)
    bQ.add(q1,BooleanClause.Occur.SHOULD)
    
    numbers = re.findall(r"[-+]?\d*\.\d+|\d+",query)
    if len(numbers) == 2:
        q2 = LatLonPoint.newDistanceQuery("Coordinates", float(numbers[0]), float(numbers[1]), 20)
        bQ.add(q2,BooleanClause.Occur.SHOULD)

    return bQ.build()

def get_tf_idf():
    with open("temp/tf.txt","r") as f:
        for line in f:
            tfs = line.strip().split("|")
            for element in tfs:
                tokens = element.split(",")
                if len(tokens) == 3:
                    tf[int(tokens[0])][tokens[1]] = tokens[2]
        f.close()

    with open("temp/idf.txt","r") as f:
        for line in f:
            idfs = line.strip().split("|")
            for element in idfs:
                tokens = element.split(",")
                if len(tokens) == 2:
                    idf[tokens[0]] = tokens[1]
        f.close()
    
# 有一个list of document，需要计算tfidf分数，
def ranking(documents):  
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


lucene.initVM()

tf = defaultdict(lambda: defaultdict(int))
idf = defaultdict(int)
tfidf = defaultdict(lambda: defaultdict(int))

get_tf_idf()

indexPath = File("index/").toPath() # create index path
indexDir = FSDirectory.open(indexPath)

# search the index
analyzer = StandardAnalyzer()
reader = DirectoryReader.open(indexDir)
searcher = IndexSearcher(reader)


while True:
    input_query = input("Please Enter a query:\n")
    input_query = remove_stopwords(input_query)
    
    query = create_query(input_query)
    print(f'Query: {query}')

    start = time.time()

    results = searcher.search(query,10)
    for hit in results.scoreDocs:
        d = reader.document(hit.doc)
        print(f'Document {hit.doc} - Score: {hit.score}')
        print('---------------------------')
        for f in d.getFields():
            name = f.name()
            print(f'{name}: {f.stringValue()}')
        
        print('---------------------------')

    end_execution()


#fields = ['processed_text','coordinate']
#occurs = [BooleanClause.Occur.SHOULD,BooleanClause.Occur.SHOULD]

#mutliField_parser = MultiFieldQueryParser(fields,analyzer)
#query = mutliField_parser.parse(input_query,fields,occurs,analyzer)

# floats, integers = extract_numbers(input_query)
# for i in integers:
#     input_query = re.sub(i,format_coordinate(int(i)),input_query)

# for i in floats:
#     input_query = re.sub(i,format_coordinate(float(i)),input_query)