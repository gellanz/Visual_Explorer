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
                }
            }
        }
}

print("Creating 'document_analyzer' index")
es.indices.create(index = 'document_analyzer', body = news_body)
print("Creating 'named_entities' index")
es.indices.create(index = 'named_entities', body = entities_body)