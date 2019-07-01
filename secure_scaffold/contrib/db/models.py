import inspect
from importlib import import_module

from secure_scaffold.config import get_setting


try:
    _DATABASE_SETTINGS = get_setting('DATABASE_SETTINGS')
except AttributeError:
    raise AttributeError('DATABASE_SETTINGS setting not defined. '
                         'For the database system to work the '
                         'DATABASE_SETTINGS setting must be defined.')


_ENGINE_KEY = _DATABASE_SETTINGS.get('engine')
if not _ENGINE_KEY:

    raise KeyError('DATABASE_SETTINGS improperly defined. '
                   'Requires an engine value.')
_ENGINE_MODULE = import_module(_DATABASE_SETTINGS['engine'])


_ENGINE_SETTINGS = _DATABASE_SETTINGS.get('settings')
if not _ENGINE_SETTINGS:
    raise KeyError('DATABASE_SETTINGS improperly defined. '
                   'Requires a settings value.')
ENGINE = _ENGINE_MODULE.Engine(**_DATABASE_SETTINGS['settings'])


class NotUniqueError(Exception):
    pass


class TooManyPrimaryKeysError(NotUniqueError):
    pass


class NoPrimaryKeyError(Exception):
    pass


class NotFoundError(Exception):
    pass


class Field:
    """
    Class used to define what type an attribute on a class Model will be.
    Example usage:
        class User(Model):
            name = Field(str)
            age = Field(int)
    """
    def __init__(self,
                 field_type,
                 default=None,
                 unique=False,
                 primary=False,
                 required=True):
        self.type = field_type
        if default is not None:
            if callable(default):
                default = default()
            if not isinstance(default, field_type):
                raise AttributeError("Default value must match the specified type {}, instead it is type {}"
                                     .format(field_type, type(default)))
        self.default = default
        self.primary = primary
        self.unique = primary or unique  # Must be unique if a primary key.
        self.required = required


class Model:
    """
    Base Model class.

    In firestore each class will represent a collection in Firestore with
    each instance of a class representing a document in the collection.

    In Datastore the `collection` attribute is used as the `kind` with each
    class instance representing an entity.

    Example usage:
        class User(Model):
            collection = 'User'
            name = Field(str, primary=True)
            age = Field(int)

        user = User(name="John", age=20).save()

        user.age = 24
        user.save()
    """

    def __init__(self, _id=None, _created_at=None, **kwargs):
        """
        Initialise the class
        :param id: ID of the document in its relevant engine.
        :param kwargs: Named arguments matching the fields defined by the class
                        All fields defined are required, unless there is a default specified
        """
        # Check the class has a collection attribute set
        try:
            self.collection
        except AttributeError:
            raise AttributeError("Attribute 'collection' must be defined")

        # Get all the Field attributes defined by the class
        # List of tuples, [ (attribute name, field class), ... ]
        fields = [item for item in inspect.getmembers(self)
                  if isinstance(item[1], Field)]
        # convert to dictionary
        self.fields = dict(fields)

        # Set id
        self._id = _id

        self._created_at = _created_at

        # For each attribute set on the model class make sure the class is instantiated with it
        # Set each attribute and save the Field class to a __meta__ attribute name
        primary_count = 0
        for attr_name, attr_class in self.fields.items():
            if attr_class.primary:
                primary_count += 1
            if primary_count > 1:
                raise TooManyPrimaryKeysError(
                    "Model %s can only support a single Primary Key" % self.__class__.__name__
                )
            if attr_name in kwargs:
                attr_value = kwargs[attr_name]

                if isinstance(attr_value, attr_class.type):
                    setattr(self, '__meta__' + attr_name, attr_class)
                    setattr(self, attr_name, attr_value)
                else:
                    raise AttributeError("Attribute {} must be type {} but instead is type {}"
                                         .format(attr_name, attr_class.type, type(attr_value)))
            else:
                if attr_class.default is not None:
                    attr_value = attr_class.default
                    setattr(self, '__meta__' + attr_name, attr_class)
                    setattr(self, attr_name, attr_value)
                elif attr_class.required:
                    raise AttributeError("Attribute {} must be defined".format(attr_name))
        if not primary_count:
            raise NoPrimaryKeyError(
                "Model %s must have a Primary Key field." % self.__class__.__name__
            )

    def __setattr__(self, key, value):
        """
        Overwrite this function so we can validate fields before they're set.

        :param key: Name of the attribute trying to be set
        :param value: Value trying to set it too
        :return: Error or sets the attribute to the value
        """
        try:
            # If we have the meta class (i.e. it is a specified Field with a type)
            attr_class = getattr(self, '__meta__' + key)
            # Check the type of the value against the specified Field type
            if isinstance(value, attr_class.type):
                super().__setattr__(key, value)
            else:
                raise TypeError("Value for {} should be type {} but is instead type {}".format(
                    key,
                    attr_class.type,
                    type(value)
                ))
        except AttributeError:
            super().__setattr__(key, value)

    def _check_unique_fields(self):
        """
        Look through the model fields and check that if one is set to be unique,
        that no other saved documents match it

        :return: Error or nothing
        """
        for attr_name, attr_class in self.fields.items():
            value = getattr(self, attr_name)
            if attr_class.unique:
                for instance in self.get(**{attr_name: value}):
                    if instance._key != self._key:
                        raise NotUniqueError(
                            "Attribute {} must be unique, but there is already a "
                            "document defined with the value {}".format(attr_name, value)
                        )

    def to_dict(self):
        """
        Convert the instance to a dictionary.

        :return: all Field attributes as a dict
        """
        attrs = {}
        for field in self.fields.keys():
            attr = getattr(self, field)
            if not isinstance(attr, Field):
                attrs[field] = getattr(self, field)
            else:
                attrs[field] = None
        return attrs

    def save(self):
        """
        Save the instance to the database.
        """
        self._check_unique_fields()
        return ENGINE.save(self)

    @property
    def pk(self):
        """
        Return the primary key of the object - this is used as the ID in the
        database.

        :return: The primary key of the object.
        """
        for attr_name, attr_class in self.fields.items():
            if attr_class.primary:
                return getattr(self, attr_name)

    @property
    def id(self):
        """
        Equivalent to `pk`.
        """
        if self._id:
            return self._id
        self._id = self.pk
        return self._id

    @property
    def _key(self):
        """
        Return the key as defined by the database engine.

        Used mainly for datastore.
        """
        key = ENGINE.key(self)
        return key

    def delete(self):
        """
        Delete self from the database.
        """
        ENGINE.delete(self)

    @classmethod
    def get(cls, id=None, **kwargs):
        """
        Yield a document or list of documents from the database

        :param id: If specified will return a list with only the specified object.
        :param kwargs: Named fields and values to match within documents
                        e.g. User.get(name="John", age=20)
        :return: Generator of the relevant documents
        """
        return ENGINE.get(cls, id, **kwargs)

    @classmethod
    def get_all(cls):
        """
        Yield all documents in this collection as a list

        :return: generator of all the docs
        """
        return ENGINE.get_all(cls)

    @classmethod
    def one(cls, id=None, **kwargs):
        """
        Return the first object with the specified filters.

        If none found raise a NotFoundError.
        """
        try:
            return next(ENGINE.get(cls, id, **kwargs))
        except StopIteration:
            raise NotFoundError("No instance of {self.__class__} with the required args found.")

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        return other.id == self.id

    def __repr__(self):
        return f'{self.__class__.__name__}(**{self.to_dict()})'
