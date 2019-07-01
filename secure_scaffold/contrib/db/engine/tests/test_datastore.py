from importlib import reload
from types import GeneratorType
from unittest import mock

import pytest

from secure_scaffold.contrib.db.engine import datastore


@pytest.fixture
def db_models():
    with mock.patch('secure_scaffold.config.get_setting') as mock_settings:
        mock_settings.return_value = {
            'engine': 'secure_scaffold.contrib.db.engine.datastore',
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
    with mock.patch('secure_scaffold.contrib.db.engine.datastore.Engine._CLIENT') as mock_datastore:
        test_engine = datastore.Engine()
        test_engine.datastore = mock_datastore
        yield test_engine


def test_key(engine: datastore.Engine, User):
    engine.client.key.return_value = 'test'
    u = User(name='test', age=1)
    key = engine.key(u)

    assert key == 'test'
    engine.client.key.assert_called_once_with(u.collection, u.id)


def assert_create_called(mock_datastore: mock.MagicMock, engine, model):
    mock_datastore.Entity.assert_called_once_with(engine.key(model))
    mock_datastore.Entity().update.assert_called()
    engine.client.put.assert_called_with(mock_datastore.Entity())
    engine.client.key.assert_called_with(model.collection, model.id)


@mock.patch('secure_scaffold.contrib.db.engine.datastore.datastore')
def test_create(mock_datastore: mock.MagicMock, engine: datastore.Engine, User):
    u = User(name='test', age=1)
    res = engine._create(u)

    assert_create_called(mock_datastore, engine, u)
    assert res == u


@mock.patch('secure_scaffold.contrib.db.engine.datastore.datastore')
def test_save_new(mock_datastore: mock.MagicMock, engine: datastore.Engine, User):
    u = User(name='test', age=1)
    res = engine.save(u)

    assert_create_called(mock_datastore, engine, u)
    assert res == u


@mock.patch('secure_scaffold.contrib.db.engine.datastore.datastore')
def test_save(mock_datastore: mock.MagicMock, engine: datastore.Engine, User):
    u = User(name='test', age=1, _created_at=True)
    res = engine.save(u)

    engine.client.key.assert_called_with(u.collection, u.id)
    mock_datastore.Entity.assert_called_with(engine.client.key())

    data = u.to_dict()
    data['_id'] = u.id

    mock_datastore.Entity().update.assert_called_once_with(data)
    engine.client.put.assert_called_once_with(mock_datastore.Entity())
    assert res == u


def test_get_with_id(engine: datastore.Engine, User):
    u = User(name='test', age=1)
    engine.client.get.return_value = u.to_dict()
    res = engine.get(User, id='test')

    assert isinstance(res, GeneratorType)

    res = list(res)

    assert len(res) == 1
    assert res == [u]

    engine.client.key.assert_called_with(User.collection, 'test')
    engine.client.get.assert_called_once_with(engine.client.key())


def test_get(engine: datastore.Engine, User):
    data = [
        {'name': 'test', 'age': 1, '_id': 'test'},
        {'name': 'test2', 'age': 2, '_id': 'test2'},
    ]
    engine.client.query().fetch.return_value = data
    res = engine.get(User, age=1, name='test')

    assert isinstance(res, GeneratorType)

    res = list(res)

    assert len(res) == 2
    assert res == [User(**item) for item in data]

    engine.client.query.assert_called_with(kind=User.collection)
    engine.client.query().add_filter.assert_called_with('name', '=', 'test')
    engine.client.query().fetch.assert_called_once()


def test_get_all(engine: datastore.Engine, User):
    engine.client.query().fetch.return_value = [
        {'name': 'test', 'age': 1, '_id': 'test'},
        {'name': 'test2', 'age': 2, '_id': 'test'},
    ]
    res = engine.get_all(User)

    assert isinstance(res, GeneratorType)

    res = list(res)
    assert len(res) == 2

    for item in res:
        assert isinstance(item, User)

    engine.client.query.assert_called_with(kind=User.collection)
    engine.client.query().fetch.assert_called_once()


def test_delete(engine: datastore.Engine, User):
    engine.client.key.return_value = 'test'
    u = User(name='test', age=1)
    engine.delete(u)

    engine.client.key.assert_called_once_with(u.collection, u.id)
    engine.client.delete.assert_called_once_with('test')
