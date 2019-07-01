from importlib import reload
from types import GeneratorType
from unittest import mock

import pytest

from secure_scaffold.contrib.db.engine import firestore


@pytest.fixture
def db_models():
    with mock.patch('secure_scaffold.config.get_setting') as mock_settings:
        mock_settings.return_value = {
            'engine': 'secure_scaffold.contrib.db.engine.firestore',
            'settings': {'project': 'null'}
        }
        from secure_scaffold.contrib.db import models
        reload(models)
        yield models


@pytest.fixture
def User(db_models):
    class User(db_models.Model):
        collection = "User"
        name = db_models.Field(str, primary=True)
        age = db_models.Field(int)
    return User


@pytest.fixture
def engine():
    with mock.patch('secure_scaffold.contrib.db.engine.firestore.Engine._CLIENT') as mock_client:
        test_engine = firestore.Engine()
        test_engine.firestore = mock_client
        yield test_engine


def test_key(engine: firestore.Engine):
    class Obj:
        id = 'test'
        collection = 'collection'
    assert engine.key(Obj) == 'collection.test'


def test_create(engine: firestore.Engine, User):
    user = User(name='test', age=1)
    engine.client.collection().add().return_value = [mock.MagicMock(), User]
    res = engine._create(user)

    engine.client.collection.assert_called_with(User.collection)
    engine.client.collection().add.assert_called_with(user.to_dict())

    assert res == user


def test_save_calls_create(engine: firestore.Engine, User):
    user = User(name='test', age=1)
    engine.client.collection().add().return_value = [mock.MagicMock(), User]
    engine.client.collection().document().get().exists = False
    res = engine.save(user)

    engine.client.collection.assert_called_with(User.collection)
    engine.client.collection().document.assert_called_with(user.id)
    engine.client.collection().document().get.assert_called()
    engine.client.collection().add.assert_called_with(user.to_dict())

    assert res == user


def test_save(engine: firestore.Engine, User):
    user = User(name='test', age=1)
    engine.client.collection().add().return_value = [mock.MagicMock(), User]
    engine.client.collection().document().get().exists = True
    user._id = 1
    res = engine.save(user)

    engine.client.collection.assert_called_with(User.collection)
    engine.client.collection().document.assert_called_with(user.id)
    engine.client.collection().document().get.assert_called()
    engine.client.collection().document().set.assert_called_once_with(user.to_dict())

    assert res == user


def test_get_with_id(engine: firestore.Engine, User):
    u = User(name='test', age=1)
    mock_user = mock.MagicMock()
    mock_user.to_dict.return_value = u.to_dict()
    mock_user.id = u.id
    mock_user.create_time.ToDateTime.return_value = 1

    engine.client.collection().document().get.return_value = mock_user
    res = engine.get(User, id=u.id)

    assert isinstance(res, GeneratorType)

    res = list(res)

    assert len(res) == 1
    assert res[0] == u

    engine.client.collection.assert_called_with(User.collection)
    engine.client.collection().document.assert_called_with(u.id)
    engine.client.collection().document().get.assert_called()


def test_get(engine: firestore.Engine, User):
    u = User(name='test', age=1)
    mock_user = mock.MagicMock()
    mock_user.to_dict.return_value = u.to_dict()
    mock_user.id = u.id
    mock_user.create_time.ToDateTime.return_value = 1

    engine.client.collection().where().where().stream.return_value = [
        mock_user,
    ]
    res = engine.get(User, age=1, name='test')

    assert isinstance(res, GeneratorType)

    res = list(res)
    assert len(res) == 1

    for item in res:
        assert isinstance(item, User)

    engine.client.collection.assert_called_with(User.collection)
    engine.client.collection().where.assert_called_with('age', '==', 1)
    engine.client.collection().where().where.assert_called_with('name', '==', 'test')
    engine.client.collection().where().where().stream.assert_called()


def test_get_all(engine: firestore.Engine, User):
    engine.client.collection().stream.return_value = [
        User(name='test', age=1),
        User(name='test2', age=2),
    ]
    res = engine.get_all(User)

    assert isinstance(res, GeneratorType)

    res = list(res)
    assert len(res) == 2

    for item in res:
        assert isinstance(item, User)

    engine.client.collection.assert_called_with(User.collection)
    engine.client.collection().stream.assert_called()


def test_delete(engine: firestore.Engine, User):
    user = User(name='test', age=1)

    engine.delete(user)
    engine.client.collection.assert_called_with(user.collection)
    engine.client.collection().document.assert_called_with(user.id)
    engine.client.collection().document().get.assert_called()
    engine.client.collection().document().get().reference.delete.assert_called()
