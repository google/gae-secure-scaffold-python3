from datetime import datetime

try:
    from google.cloud import datastore
except ImportError:
    raise ImportError("Can't use the datastore engine without "
                      "google-cloud-datastore installed. Please "
                      "pip install google-cloud-datastore and then"
                      "try again.")

from secure_scaffold.contrib.db.engine.base import BaseEngine


class Engine(BaseEngine):
    _CLIENT = datastore.Client

    def key(self, model):
        """
        Create a unique identifier for getting Datastore Entities.
        """
        return self.client.key(model.collection, model.id)

    def _create(self, model):
        """
        Create document in the Datastore and return the model.
        """
        entity = datastore.Entity(self.key(model))
        data = model.to_dict()
        data['_created_at'] = datetime.now()
        data['_id'] = model.id
        entity.update(data)
        self.client.put(entity)
        model.created_time = data['_created_at']

        return model

    def save(self, model):
        """
        Save a document to the Datastore.

        If it doesn't already exist create a new one and return it.

        If it does exist update it in the Datastore and return it.
        """
        if not model._created_at:
            return self._create(model)
        data = model.to_dict()
        data['_id'] = model.id
        entity = datastore.Entity(
            self.key(model)
        )
        entity.update(data)
        self.client.put(entity)
        return model

    def get(self, model, id=None, **kwargs):
        """
        Get all documents from Datastore with the given arguments.

        If given id as an argument we try to yield only a single document.

        If any other arguments are given we generate filters on top
        of the initial query before fetching it.

        Yields the found documents.

        :param id: A unique identifier for a document.
        :param kwargs: Arbitrary mapping of arguments to document fields.
        :return: A generator with the found documents.
        """
        if id:
            key = self.client.key(model.collection, id)
            entity = self.client.get(key)
            yield model(id=id, **entity)

        else:
            query = self.client.query(kind=model.collection)

            for key, value in kwargs.items():
                query.add_filter(key, '=', value)

            for doc in query.fetch():
                yield model(id=doc['_id'], **doc)

    def get_all(self, model):
        """
        Yield all the documents in this collection.

        :return: A generator with the found documents.
        """
        docs = self.client.query(kind=model.collection).fetch()
        for doc in docs:
            yield model(id=doc['_id'], **doc)

    def delete(self, model):
        """
        Delete the document from the Datastore.

        :param model: The model instance to delete.
        """
        self.client.delete(self.key(model))
