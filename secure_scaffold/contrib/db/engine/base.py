class BaseEngine:
    _CLIENT = None

    def __init__(self, **kwargs):
        self.client = self._CLIENT(**kwargs)

    def key(self, model):
        raise NotImplementedError()

    def get(self, model, id=None, **kwargs):
        """
        Get and yield a filtered list of documents from the
        databased filtered by the kwargs. If id is given yield a single
        object as id should be unique - override in the subclass.
        """
        raise NotImplementedError()

    def _create(self, model):
        """
        Create a document - override in the subclass.
        """
        raise NotImplementedError()

    def save(self, model):
        """
        Save a document (should be safe for both creation and updating) -
        override in the subclass.
        """
        raise NotImplementedError()

    def get_all(self, model):
        """
        Get and yield all the documents from the database - override in the subclass.
        """
        raise NotImplementedError()

    def delete(self, model):
        """
        Delete the document from the database - override in the subclass.
        """
        raise NotImplementedError()
