try:
    from google.cloud import firestore
except ImportError:
    raise ImportError("Can't use the firestore engine without "
                      "google-cloud-firestore installed. Please "
                      "pip install google-cloud-firestore and then"
                      "try again.")

from secure_scaffold.contrib.db.engine.base import BaseEngine


class Engine(BaseEngine):
    _CLIENT = firestore.Client

    def key(self, model) -> str:
        """
        This is mostly intended for Datastore but can still feasibly be used with
        Firestore as a unique identifier.

        Combines the model collection and id to create a unique identifier across
        models.
        """
        return f'{model.collection}.{model.id}'

    def _create(self, model):
        """
        Create document in the Firestore, add the created timestamp to the model.

        Return the model.
        """
        doc = self.client.collection(model.collection).add(model.to_dict())
        model._created_at = doc[0].ToDatetime()

        return model

    def save(self, model):
        """
        Check if a document already exists in the Firestore. If not create a new one.
        If there is one update it.

        Return the model.
        """
        document = self.client.collection(model.collection).document(model.id)
        if document.get().exists:
            document.set(model.to_dict())
            return model
        self._create(model)
        return model

    def get(self, model, id=None, **kwargs):
        """
        Get all documents from Firestore with the given arguments.

        If given id as an argument we try to yield only a single document.

        If any other arguments are given we generate where statements on top
        of the initial query before streaming it.

        Yields the found documents.

        :param id: A unique identifier for a document.
        :param kwargs: Arbitrary mapping of arguments to document fields.
        :return: A generator with the found documents.
        """
        if id:
            doc = self.client.collection(model.collection).document(id).get()
            yield model(id=doc.id, date=doc.create_time.ToDatetime(), **doc.to_dict())
        else:
            doc = self.client.collection(model.collection)
            for key, value in kwargs.items():
                doc = doc.where(key, '==', value)
            docs = doc.stream()

            for doc in docs:
                yield model(id=doc.id, date=doc.create_time.ToDatetime(), **doc.to_dict())

    def get_all(self, model):
        """
        Yield all the documents in this collection.

        :return: A generator with the found documents.
        """
        docs = self.client.collection(model.collection).stream()
        for doc in docs:
            yield model(id=doc.id, **doc.to_dict())

    def delete(self, model):
        """
        Delete the document from the collection.

        :param model: The model instance to delete.
        """
        instance = self.client.collection(model.collection).document(model.id).get()
        instance.reference.delete()
