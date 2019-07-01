from secure_scaffold.contrib.db import models


class User(models.Model):
    collection = 'user'
    name = models.Field(str, primary=True)
    age = models.Field(int, required=False)
    data = models.Field(dict, required=False)

