import lucene
from java.io import *
from org.apache.lucene.search import IndexSearcher
from org.apache.lucene.store import SimpleFSDirectory, FSDirectory
from org.apache.lucene.queryparser.classic import QueryParser
from org.apache.lucene.analysis.en import EnglishAnalyzer
from org.apache.lucene.index import DirectoryReader
from indexing import remove_stopwords
from collections import defaultdict

def get_tf_idf():
    with open("temp/tf.txt","r") as f:
        for line in f:
            tfs = line.split("|")
            for element in tfs:
                tokens = element.split(",")
                if len(tokens) == 3:
                    tf[int(tokens[0])][tokens[1]] = tokens[2]
        f.close()

    with open("temp/idf.txt","r") as f:
        for line in f:
            idfs = line.split("|")
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
reader = DirectoryReader.open(indexDir)
searcher = IndexSearcher(reader)

query = "example query is an apple"
query = remove_stopwords(query)
search_field = "text"
analyzer = EnglishAnalyzer()
query = QueryParser(search_field,analyzer).parse(query)

results = searcher.search(query,10)
for hit in results.scoreDocs:
    d = reader.document(hit.doc)
    print(f'Document {hit.doc} - Score: {hit.score}')
    print('---------------------------')
    for f in d.getFields():
        print(f'{f.name()}: {f.stringValue()}')
    
    print('---------------------------')
