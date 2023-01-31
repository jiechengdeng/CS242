import lucene
from org.apache.lucene import index, search
from org.apache.lucene.search import spans
from lupyne.engine import Query
from org.apache.lucene.store import SimpleFSDirectory, FSDirectory
from collections import defaultdict

def get_tf_idf():
    with open("temp/tf.txt","r") as f:
        for line in f:
            tfs = line.split("|")
            for element in tfs:
                if tfs == "\n":
                    continue
                tokens = element.split(",")
                tf[int(tokens[0])][tokens[1]] = tokens[2]
        f.close()

    with open("temp/idf.txt","r") as f:
        for line in f:
            idfs = line.split("|")
            for element in idfs:
                if idfs == "\n":
                    continue
                tokens = element.split(",")
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

indexPath = File("index/").toPath() # create index path
indexDir = FSDirectory.open(indexPath)

# search the index
reader = DirectoryReader.open(indexDir)