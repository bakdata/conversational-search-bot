import logging
from abc import ABC, abstractmethod
from typing import Text, Dict, List, Any, Optional

from elasticsearch import Elasticsearch
from rasa_sdk.knowledge_base.storage import KnowledgeBase

logger = logging.getLogger(__name__)


class Attribute(ABC):

    @abstractmethod
    def get_field(self, document: Dict[Text, Any]) -> Any:
        pass

    @abstractmethod
    def generate_query(self, value: Text, role: Text) -> Dict:
        pass


def generate_term_query(attribute: Text, value: Text) -> Dict:
    return {
        "fuzzy": {
            attribute: {
                "value": value
            }
        }
    }


def generate_match_query(attribute: Text, value: Text) -> Dict:
    return {
        "match": {
            attribute: {
                "query": value
            }
        }
    }

def generate_match_phrase_query(attribute: Text, value: Text) -> Dict:
    return {
        "match_phrase": {
            attribute: {
                "query": value
            }
        }
    }


def generate_range_query(attribute: Text, value: Text, role: Text) -> Dict:
    return {
        "range": {
            attribute: {
                role: value
            }
        }
    }


class DefaultAttribute(Attribute):

    def __init__(self, name: str) -> None:
        self._name: str = name

    def get_field(self, document: Dict[Text, Any]) -> Any:
        return document.get(self._name)

    def generate_query(self, value: Text, role: Text) -> Dict:
        return generate_match_query(self._name, value)


class TextAttribute(DefaultAttribute):
    def generate_query(self, value: Text, role: Text) -> Dict:
        return generate_match_phrase_query(self._name, value)


class RangeAttribute(DefaultAttribute):

    def generate_query(self, value: Text, role: Text) -> Dict:
        if role == 'eq':
            return generate_match_query(self._name, value)

        return generate_range_query(self._name, value, role)


class DocumentType(ABC):

    def __init__(self, index: Text, attributes: Dict[Text, Attribute]):
        self.index: Text = index
        self.attributes: Dict[Text, Attribute] = attributes

    @abstractmethod
    def to_string(self, document: Dict[Text, Any]) -> Text:
        pass


class ElasticsearchKnowledgeBase(KnowledgeBase):
    def __init__(self, document_types: Dict[Text, DocumentType],
        es: Elasticsearch) -> None:
        self.document_types: Dict[Text, DocumentType] = document_types
        self.es = es
        super().__init__()

    def to_kb_obj(self, obj, object_type: Text) -> Dict[Text, Any]:
        source = obj["_source"]
        document_type = self.document_types[object_type]
        pretty = document_type.to_string(source)
        id_ = obj['_id']
        name = f"{pretty}"
        kb_obj = {name: attribute.get_field(source) for name, attribute in
                  document_type.attributes.items()}
        kb_obj['name'] = name
        kb_obj['id'] = id_
        return kb_obj

    async def get_attributes_of_object(self, object_type: Text) -> List[Text]:
        if object_type not in self.document_types:
            return []

        return [attribute for attribute in
                self.document_types[object_type].attributes.keys()]

    async def get_objects(
        self, object_type: Text, attributes: List[Dict[Text, Text]],
        limit: int = 5
    ) -> List[Dict[Text, Any]]:
        if object_type not in self.document_types:
            return []

        document_type = self.document_types[object_type]
        queries = [
            document_type.attributes[attribute["name"]].generate_query(
                attribute["value"], attribute.get("role", None))
            for attribute in attributes]
        query = {
            "size": limit,
            "query": {
                "bool": {
                    "must": queries
                }
            }
        }

        logger.info(f"Searching for {object_type} using {query}")
        index = document_type.index
        res = self.es.search(index=index, body=query)
        return [self.to_kb_obj(hit, object_type) for hit in res['hits']['hits']]

    async def get_object(
        self, object_type: Text, object_identifier: Text
    ) -> Optional[Dict[Text, Any]]:
        if object_type not in self.document_types:
            return None

        logger.info(f"Retrieving {object_identifier} from {object_type}")
        document_type = self.document_types[object_type]
        index = document_type.index
        obj = self.es.get(index=index, id=object_identifier)
        if obj:
            return self.to_kb_obj(obj, object_type)
        else:
            return None
