from whoosh.qparser import *
from whoosh.fields import Schema, TEXT, KEYWORD, NUMERIC
from whoosh.analysis import StandardAnalyzer
from whoosh import index
import os.path

# year,author,title,abstract are 字段，每隔字段对应索引查找标准文件的一部分信息
schema = Schema(year=NUMERIC(stored=True),
                author=TEXT(analyzer=StandardAnalyzer(stoplist=None), stored=True),
                title=TEXT(analyzer=StandardAnalyzer(stoplist=None), stored=True),
                abstract=TEXT(analyzer=StandardAnalyzer(stoplist=None), stored=True),
                body=TEXT(analyzer=StandardAnalyzer(stoplist=None)),
                subject=KEYWORD(commas=True, scorable=True),
                keywords=KEYWORD(commas=True, scorable=True))

# to create an index in a dictionary if there is none
if not os.path.exists("indexdir"):
    os.mkdir("indexdir")
ix = index.create_in("indexdir", schema)

# open an existing index object
ix = index.open_dir("indexdir")

# create a writer object to add documents to the index
writer = ix.writer()

# now we can add documents to the index
abstract1 = ("It depicts the struggles of young Scarlett O'Hara, the spoiled daughter of a well-to-do plantation owner, who must use every means at her disposal to claw her way out of poverty following Sherman's destructive 'March to the Sea'. This historical novel features a Bildungsroman or coming-of-age story, with the title taken from a poem written by Ernest Dowson")

abstract2 = ("Children's and Household Tales (German: Kinder- und Hausmärchen) is a collection of fairy tales first published in 20 December 1812 by the Grimm brothers, Jacob and Wilhelm. The collection is commonly known in English as Grimms' Fairy Tales.")

writer.add_document(year=u"1936",
                    author="Margaret Mitchell",
                    title=u"Gone with the wind",
                    abstract=abstract1,
                    subject=u"novel, love",
                    keywords=u"Scarlett, Rhett")
writer.add_document(year=u"1812",
                    author=u" Jacob and Wilhelm",
                    title=u"Grimms' Fairy Tales",
                    abstract=abstract2,
                    subject=u"story, children",
                    keywords=u"The Frog King,  Rapunzel")

# close the writer and save the added documents in the index
# you should call the commit() function once you finish adding the documents otherwise you will cause an error-
# when you try to edit the index next time and open another writer.
writer.commit()

# parsing the query
# this is just a simple parser with default field
parser = QueryParser("abstract", schema=schema)

# if you want “unfielded” terms to search both the title and content fields,  use a whoosh.qparser.MultifieldParser
# parser = MultifieldParser(["title", "abstract"], schema=schema)
# call parse() on query to parse a query string into a query object
result = parser.parse(u"apple company department")
print(result)

# by default, the parser treats the words as if they were connected by AND.
# Changing the "group" keyword argument if you want it connencted by Or.
# parser = MultifieldParser(["title", "abstract"], schema=schema,group=OrGroup)
result = parser.parse(u"apple company department")
print(result)

# you can use .add_plugin() to make the parser more powerful
# GtLtPlugin() lets you use >, <, >=, <=, =>, or =< after a field specifier,
# and translates the expression into the equivalent range:
parser.add_plugin(GtLtPlugin())
result = parser.parse(u"year:<2000")
print(result)


# FuzzyTermPlugin lets you search for “fuzzy” terms, that is, terms that don’t have to match exactly.
# The fuzzy term will match any similar term within a certain number of “edits”
parser.add_plugin(FuzzyTermPlugin())
result = parser.parse(u"author:margare~")  # would match a document has Margare and all terms in the index within one “edit” of cat, for example Margaret insert t
print(result)
# searcher object is used for searching the matched documents
# you can open the searcher using a with statement so the searcher is automatically closed when you’re done with it
# ix is the document index we created before
with ix.searcher() as searcher:
    results = searcher.search(result)  # The Results object acts like a list of the matched documents.
    print(results[0])

# The default phrase query tokenizes the text between the quotes and creates a search for those terms in proximity.
# print parser.default_set()
# use single quotation marks for the unicode string since double quotation marks are used to represent phrases here
result = parser.parse(u'title:"gonE the"~2')  # would match a document has wind within 2 words after gone
print(result)
with ix.searcher() as searcher:
    results = searcher.search(result)
    print(results)

# you can use * or ? for inexact term search
# use ? to represent a single character and * to represent any number of characters
result = parser.parse(u'title:go*')  # would match a document has wind within 2 words after gone
print(result)
with ix.searcher() as searcher:
    results = searcher.search(result)
    print(results)
    print(results[0])

# If you want to do more complex proximity searches,
# you can replace the phrase plugin with the whoosh.qparser.SequencePlugin.
# It allows any query between the quotes.

# remove the ability to specify phrase queries inside double quotes.
parser.remove_plugin_class(PhrasePlugin)
# Adds the ability to group arbitrary queries inside double quotes,
# to produce a query matching the individual sub-queries in sequence.
parser.add_plugin(SequencePlugin())
# IMPORTANT!!! Not like phrase query which specify the field outside the double quotation marks,
# you need to specify the field inside the double quotation marks for each subquery
# the query string below represents the query 'abstract:"(child OR childr*) ho*sehold"~3 AND title:tales'
result = parser.parse(u'"abstract:(child OR childr*) abstract:ho*sehold"~3 AND title:tale*')
print(result)
with ix.searcher() as searcher:
    results = searcher.search(result)
    print(results)
# print(results[0])
    # we can get the position of a term by doing it manually
    import re
    for result in results:
        analyzer = StandardAnalyzer(stoplist=None)
        a = [(t.pos) for t in analyzer(result['abstract'], positions=True) if re.match(r"tale*", t.text)]
        print("the position of the word pattern "+"<tale*> "+"in document <"+result['title']+"> is:")
        print(a)
