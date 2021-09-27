from elasticsearch import Elasticsearch

es = Elasticsearch('localhost:9200', timeout=300)

news_body = {
    "mappings": {
            "properties": {
                "idDocument": {
                    "type": "long"
                },
                "sourceName": {
                    "type": "text"
                },
                "publicationDate": {
                    "type": "date"
                },
                "title": {
                    "type": "text"
                },
                "originalContent": {
                    "type": "text"
                },
                "category": {
                    "type": "text"
                },
                "content": {
                    "type": "text",
                    "analyzer": "whitespace"
                },
                # Los siguientes campos son de los agregados posteriormente. Manual tecnico M. Yadira pag. 12
                "categoryKW": {
                     "type": "keyword"
                },
                "contentWsTk": {
                     "type": "text",
                     "analyzer": "whitespace" 
                },
                "documentURL": {
                     "type": "text"
                },
                "imageURL": { 
                     "type": "text" 
                },
                "contentFD": { 
                     "type": "text",
                     "fielddata": True 
                },
                "categoryMLP": { 
                     "type": "keyword" 
                },
                "sourceNameKW": {
                     "type": "keyword" 
                }
            }
        }
}


entities_body = {
    "mappings": {
            "properties": {
                "idDocEntity": {
                    "type": "long"
                },
                "idDocument": {
                    "type": "long"
                },
                "entity": {
                    "type": "text"
                },
                "catEntity": {
                    "type": "text"
                },
                # Los siguientes campos son de los agregados posteriormente. Manual tecnico M. Yadira pag. 12
                "catEntityKW": { 
                    "type": "keyword" 
                },
                "entityKW": { 
                    "type": "keyword" 
                },
            }
        }
}



print("Creating 'document_analyzer' index")
es.indices.create(index = 'document_analyzer', body = news_body)
print("Creating 'named_entities' index")
es.indices.create(index = 'named_entities', body = entities_body)

# POST _update_by_query, checar manual técnico M. Yadira pag. 12

update_query_news = {
    "query": { 
        "constant_score" : { 
            "filter" : { 
                "exists" : {
                    "field" : "category" 
                } 
            } 
        } 
    }, 
    "script" : {
        "source": "ctx._source.categoryKW = ctx._source.category;" 
        }
}
print("Updating by query")
es.update_by_query(body=update_query_news, index='document_analyzer')

update_query_news = {
    "query":{ 
        "constant_score":{ 
            "filter":{ 
                "exists": {
                    "field":"content"
                } 
            }
        }
    },
    "script":{ 
        "source":"ctx._source.contentWsTk = ctx._source.content;" }
}
print("Updating by query")
es.update_by_query(body=update_query_news, index='document_analyzer')

update_query_news = {
    "query":{ 
        "constant_score":{ 
            "filter":{
                "exists": {
                    "field":"content"
                } 
            } 
        } 
    }, 
    "script":{
        "source":"ctx._source.contentFD = ctx._source.content;" }
}
print("Updating by query")
es.update_by_query(body=update_query_news, index='document_analyzer')

update_query_news = {
    "query":{ 
        "constant_score":{ 
            "filter":{
                "exists": {
                    "field":"sourceName"
                } 
            } 
        } 
    }, 
    "script":{
        "source": "ctx._source.sourceNameKW = ctx._source.sourceName;"}
}
print("Updating by query")
es.update_by_query(body=update_query_news, index='document_analyzer')

# http://localhost:5601/app/management/data/index_management/indices
# http://localhost:5601/app/dev_tools#/console?load_from=https:/www.elastic.co/guide/en/elasticsearch/reference/current/snippets/2215.console