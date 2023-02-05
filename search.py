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
    numbers = re.findall(r"[-]?\d*\.\d+|[-]?\d+",query)
    integers = []
    floats = []
    for i in numbers:
        if '.' in i:
            floats.append(i)
        else:
            integers.append(i)
    return floats, integers

def read_text():
    text = {}
    with open("temp/tweet_text.txt","r") as file:
        start = False
        t = ""
        id = None
        first = True
        for line in file:
            element = line.strip().split("^&&^||@@#$@@")
            if len(element) == 2:
                start = False        
            if first:
                t += element[1]
                id = element[0]
                start = True
                first = False
            if not start and len(element) == 2:
                text[id] = t
                t = element[1]
                id = element[0]
                start = True
            elif start:
                t += line
        if id not in text:
            text[id] = t
    file.close()
    return text

def check_lat_lon(cor):
    if (cor[0] >= -90.0 and cor[0] <= 90.0) and (cor[1] >= -180.0 and cor[1] <= 180.0):
        return True
    return False

def create_query(query):
    bQ = BooleanQuery.Builder()
    fields = ['processed_text','User','City','Country','hashtags','url']
    occurs = [BooleanClause.Occur.SHOULD for i in range(len(fields))]

    mutliField_parser = MultiFieldQueryParser(fields,analyzer)
    q1 = mutliField_parser.parse(input_query,fields,occurs,analyzer)
    #q1 = QueryParser('processed_text',analyzer).parse(query)
    bQ.add(q1,BooleanClause.Occur.SHOULD)
    
    numbers = re.findall(r"[-]?\d*\.\d+|[-]?\d+",query)
    if len(numbers) == 2:
        numbers[0] = float(numbers[0])
        numbers[1] = float(numbers[1])
        if check_lat_lon(numbers):
            q2 = LatLonPoint.newDistanceQuery("Coordinates", numbers[0], numbers[1], 100000.0)
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
    
"""
TODO: Implement another rank algorithm like: BM25, LM
"""
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

original_text = read_text()

indexPath = File("index/").toPath() # create index path
indexDir = FSDirectory.open(indexPath)

# search the index
analyzer = StandardAnalyzer()
reader = DirectoryReader.open(indexDir)
searcher = IndexSearcher(reader)


while True:
    input_query = input("Please Enter a query:\n")
    # replace all non-alphanumeric characters
    input_query = re.sub(r'[^0-9a-zA-Z]+'," ",input_query)
    input_query = remove_stopwords(input_query)
    print(input_query)
    if input_query == "":
        continue
    query = create_query(input_query)
    print(f'Query: {query}\n')

    start = time.time()

    results = searcher.search(query,10)

    print(f'Top 10 matched documents')
    for hit in results.scoreDocs:
        d = reader.document(hit.doc)
        print(f'Document {hit.doc} - Score: {hit.score}')
        print('---------------------------')
        tid = ""
        for f in d.getFields():
            name = f.name()
            print(f'{name}: {f.stringValue()}')
            if name == "Tweet_ID":
                tid = f.stringValue()
        
        print(f'Text: {original_text[tid]}')
        
        print('---------------------------')
        print("\n")

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