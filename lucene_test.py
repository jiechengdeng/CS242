import lucene
from java.io import *
from org.apache.lucene.analysis.tokenattributes import CharTermAttribute
from org.apache.lucene.analysis.standard import StandardAnalyzer
from org.apache.lucene.analysis.en import EnglishAnalyzer
from org.apache.lucene.analysis.core import WhitespaceAnalyzer, SimpleAnalyzer, StopAnalyzer
import org.apache.lucene.document as document
from org.apache.lucene.index import IndexWriter, IndexWriterConfig
from org.apache.lucene.store import SimpleFSDirectory, FSDirectory

lucene.initVM()
# FSDirectory: store index on disk
# RAMDirectory: store index on ram

##############Analyzer#################

test = 'The quick brown fox jumped over the lazy dog'
print('English Analyzer')
analyzer = EnglishAnalyzer()
stream = analyzer.tokenStream("",StringReader(test))
stream.reset()
tokens = []
while stream.incrementToken():
    # current token = stream.getAttribute(CharTermAttribute.class_).toString() 
    tokens.append(stream.getAttribute(CharTermAttribute.class_).toString())
print(tokens)

print('Stopword Analyzer')
analyzer = StopAnalyzer() # need to provide a set of stop words 
stream = analyzer.tokenStream("",StringReader(test))
stream.reset()
tokens = []
while stream.incrementToken():
    tokens.append(stream.getAttribute(CharTermAttribute.class_).toString())
print(tokens)

print('Standard Analyzer')
analyzer = StandardAnalyzer()
stream = analyzer.tokenStream("",StringReader(test))
stream.reset()
tokens = []
while stream.incrementToken():
    tokens.append(stream.getAttribute(CharTermAttribute.class_).toString())
print(tokens)


##############Indexing#################

def indexSinglePlot(title,content):
    doc = document.Document() # Lucene Document
    # set fields and map with values for the document
    doc.add(document.Field('title',title,document.TextField.TYPE_STORED)) 
    doc.add(document.Field('content',content,document.TextField.TYPE_STORED))
    # add the document to IndexWriter
    # will generate following files:
    # fdm, fdt, temp files, write.lock
    writer.addDocument(doc)

indexPath = File("index/").toPath()
indexDir = FSDirectory.open(indexPath)
writerConfig = IndexWriterConfig(StandardAnalyzer())
writer = IndexWriter(indexDir,writerConfig)

indexSinglePlot('test','I am rich')
writer.close()



#1111
