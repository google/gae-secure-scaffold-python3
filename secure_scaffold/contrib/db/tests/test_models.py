from importlib import reload
from itertools import cycle
from unittest import mock

import pytest


pytestmark = pytest.mark.modelstest


@pytest.fixture(params=[
    'secure_scaffold.contrib.db.engine.datastore',
    'secure_scaffold.contrib.db.engine.firestore',
])
def db_models(request):
    with mock.patch('secure_scaffold.config.get_setting') as mock_settings:
        mock_settings.return_value = {
            'engine': request.param,
            'settings': {'project': 'null'}
        }
        from secure_scaffold.contrib.db import models
        reload(models)
        yield models


def test_import_bad_settings():
    with pytest.raises(AttributeError):
        from secure_scaffold.contrib.db import models
        reload(models)

    with mock.patch('secure_scaffold.config.get_setting') as mock_settings:
        mock_settings.return_value = {}
        with pytest.raises(KeyError):
            from secure_scaffold.contrib.db import models
            reload(models)
        mock_settings.return_value = {'engine': 'secure_scaffold.contrib.db.engine.datastore'}
        with pytest.raises(KeyError):
            from secure_scaffold.contrib.db import models
            reload(models)


def test_field_no_default(db_models):
    field = db_models.Field(str)
    assert field.type == str
    assert type("Im a string") == field.type
    assert field.default is None
    assert field.unique is False


def test_field_default_callable(db_models):
    a = db_models.Field(str, default=lambda: 'test')
    assert a.default == 'test'


def test_field_unique(db_models):
    field = db_models.Field(str, unique=True)
    assert field.type == str
    assert type("Im a string") == field.type
    assert field.default is None
    assert field.unique is True


def test_field_correct_default(db_models):
    field = db_models.Field(str, default="Im a string")
    assert field.type == str
    assert type("Im a string") == field.type
    assert field.default == "Im a string"
    assert type(field.default) == field.type
    assert field.unique is False


def test_field_incorrect_default(db_models):
    with pytest.raises(AttributeError):
        try:
            db_models.Field(str, default=10)
        except AttributeError as err:
            assert "Default value must match the specified type {}, instead it is type {}".format(str, int) in err.args
            raise err


def test_base_model_no_collection(db_models):
    with pytest.raises(AttributeError):
        try:
            db_models.Model()
        except AttributeError as err:
            assert "Attribute 'collection' must be defined" in err.args
            raise err


def test_base_model_get_no_collection(db_models):
    with pytest.raises(AttributeError):
        list(db_models.Model.get())


@pytest.fixture
def empty_user(db_models):
    class User(db_models.Model):
        pass
    return User


@pytest.fixture
def collection_user(db_models):
    class User(db_models.Model):
        collection = "User"
        id_attr = db_models.Field(int, primary=True)
    return User


@pytest.fixture
def user(db_models):
    class User(db_models.Model):
        collection = "User"
        name = db_models.Field(str, primary=True)
        age = db_models.Field(int)
    return User


def test_child_model_no_collection(empty_user):
    with pytest.raises(AttributeError):
        try:
            empty_user()
        except AttributeError as err:
            assert "Attribute 'collection' must be defined" in err.args
            raise err


def test_child_model_collection(collection_user):
    user = collection_user(id_attr=1)
    assert user.collection == "User"


def test_child_model_creation(user):
    user = user(name="John", age=20)
    assert user.collection == "User"
    assert user.name == "John"
    assert user.age == 20

    user.name = "Jane"
    user.age = 10

    assert user.name == "Jane"
    assert user.age == 10


def test_child_model_updating_wrong_type(user):
    user = user(name="John", age=20)
    assert user.collection == "User"
    assert user.name == "John"
    assert user.age == 20

    with pytest.raises(TypeError):
        try:
            user.name = 10
        except TypeError as err:
            assert "Value for name should be type {} but is instead type {}".format(str, int) in err.args
            raise err


def test_child_model_creation_error_missing(user):
    with pytest.raises(AttributeError):
        try:
            user(name="John")
        except AttributeError as err:
            assert "Attribute age must be defined" in err.args
            raise err


def test_child_model_creation_error_incorrect(user):
    with pytest.raises(AttributeError):
        try:
            user(name=10, age=10)
        except AttributeError as err:
            assert "Attribute name must be type {} but instead is type {}".format(str, int) in err.args
            raise err


@mock.patch('secure_scaffold.contrib.db.models.ENGINE')
def test_child_model_deletion(mock_engine, user):
    mock_engine.key.return_value = "key"
    user = user(name="John", age=20)
    user.delete()

    mock_engine.delete.assert_called_once_with(user)


@mock.patch('secure_scaffold.contrib.db.models.ENGINE')
def test_child_model_save(mock_engine, user):
    user = user(name="John", age=20)
    user.save()
    mock_engine.save.assert_called_once_with(user)
    assert user.collection == "User"
    assert user.name == "John"
    assert user.age == 20


@mock.patch('secure_scaffold.contrib.db.models.ENGINE')
def test_child_model_create(mock_engine, user):
    user = user(name="John", age=20)
    user.save()
    mock_engine.save.assert_called_once_with(user)
    assert user.collection == "User"
    assert user.name == "John"
    assert user.age == 20


@mock.patch('secure_scaffold.contrib.db.models.ENGINE')
def test_child_model_get_one(mock_engine, user):
    mock_engine.get.return_value = user(1, name="John", age=20)
    user_obj = user.get(id=1)

    mock_engine.get.assert_called_with(user, 1)
    assert isinstance(user_obj, user)
    assert user_obj.id == 1
    assert user_obj.collection == "User"
    assert user_obj.name == "John"
    assert user_obj.age == 20


@mock.patch('secure_scaffold.contrib.db.models.ENGINE')
def test_child_model_get_multiple(mock_engine, user):
    mock_engine.get.return_value = [user(1, name="John", age=20), user(2, name="Jane", age=20)]
    users = user.get(age=20)

    mock_engine.get.assert_called_once_with(user, None, age=20)

    assert len(users) == 2
    assert isinstance(users[0], user)
    assert users[0].id == 1
    assert users[0].collection == "User"
    assert users[0].name == "John"
    assert users[0].age == 20
    assert isinstance(users[1], user)
    assert users[1].id == 2
    assert users[1].collection == "User"
    assert users[1].name == "Jane"
    assert users[1].age == 20


@mock.patch('secure_scaffold.contrib.db.models.ENGINE')
def test_child_model_get_all(mock_engine, user):
    mock_engine.get_all.return_value = [user(1, name="John", age=20), user(2, name="Jane", age=20)]
    users = user.get_all()

    mock_engine.get_all.assert_called_once_with(user)

    assert len(users) == 2
    assert isinstance(users[0], user)
    assert users[0].id == 1
    assert users[0].collection == "User"
    assert users[0].name == "John"
    assert users[0].age == 20
    assert isinstance(users[1], user)
    assert users[1].id == 2
    assert users[1].collection == "User"
    assert users[1].name == "Jane"
    assert users[1].age == 20


@pytest.fixture
def unique_user(db_models):
    class User(db_models.Model):
        collection = "User"
        name = db_models.Field(str, primary=True)
        age = db_models.Field(int)
    return User


@mock.patch('secure_scaffold.contrib.db.models.ENGINE.client')
def test_unique_field_works(mock_client, unique_user):
    mock_client.collection().where().get.return_value = []

    user = unique_user(name="John", age=10)
    assert user.name == "John"
    assert user.age == 10


@mock.patch('secure_scaffold.contrib.db.models.ENGINE')
def test_unique_field_error(mock_engine, unique_user):
    from secure_scaffold.contrib.db.models import NotUniqueError
    mock_engine.get.return_value = [unique_user(1, name="John", age=20)]
    mock_engine.key.side_effect = cycle([1, 2])

    with pytest.raises(NotUniqueError):
        try:
            john = unique_user(name="John", age=10)
            john.save()
        except NotUniqueError as err:
            assert "Attribute name must be unique, but there is already a" \
                   " document defined with the value John" in err.args
            raise err


@mock.patch('secure_scaffold.contrib.db.models.ENGINE')
def test_unique_field_error_same_instance(mock_engine, unique_user):
    mock_engine.get.return_value = [unique_user(1, name="John", age=20)]
    mock_engine.key.return_value = 1

    john = unique_user(name="John", age=10)
    john.save()


def test_model_pk(user):
    test_user = user(name='test', age=1)
    assert test_user.pk == 'test'


def test_model_id(user):
    test_user = user(name='test', age=1)
    assert test_user.id == 'test'


def test_model_given_id(user):
    test_user = user(_id='my id', name='test', age=1)
    assert test_user.id == 'my id'


def test_model_to_dict(user):
    test_user = user(name='test', age=1)
    assert test_user.to_dict() == {'name': 'test', 'age': 1}


def test_model_eq_other_type(user):
    test_user = user(name='test', age=1)
    assert not test_user == 1


def test_model_assigns_default(db_models):
    class User(db_models.Model):
        collection = 'user'
        name = db_models.Field(str, primary=True, default='test')

    u = User()
    assert u.name == 'test'

    u2 = User(name='test2')
    assert u2.name == 'test2'


def test_too_many_primary_keys(db_models):
    class User(db_models.Model):
        collection = 'user'
        name = db_models.Field(str, primary=True)
        age = db_models.Field(int, primary=True)

    with pytest.raises(db_models.TooManyPrimaryKeysError):
        User(name='test', age=1)


def test_no_primary_keys(db_models):
    class User(db_models.Model):
        collection = 'user'
        name = db_models.Field(str)
        age = db_models.Field(int)

    with pytest.raises(db_models.NoPrimaryKeyError):
        User(name='test', age=1)


def test_not_required(db_models):
    class User(db_models.Model):
        collection = 'user'
        name = db_models.Field(str, primary=True)
        age = db_models.Field(int, required=False)

    User(name='test')


@mock.patch('secure_scaffold.contrib.db.models.ENGINE')
def test_one(mock_engine: mock.MagicMock, user):
    test_user = user(name='test', age=1)
    mock_engine.get.return_value = (user for user in [test_user])
    res = user.one()

    mock_engine.get.assert_called_once()
    assert res == test_user


@mock.patch('secure_scaffold.contrib.db.models.ENGINE')
def test_one_none(mock_engine: mock.MagicMock, db_models, user):
    mock_engine.get.side_effect = db_models.NotFoundError

    with pytest.raises(db_models.NotFoundError):
        user.one()

    mock_engine.get.assert_called_once()
