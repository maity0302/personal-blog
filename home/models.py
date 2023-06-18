# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from typing import Any
from django.db import models
from datetime import datetime, timedelta
from ckeditor.fields import RichTextField


class User(models.Model):
    firstname = models.CharField(db_column='firstName', max_length=50)
    lastname = models.CharField(db_column='lastName', max_length=50)
    username = models.CharField(max_length=25, null=False)
    email = models.EmailField(max_length=50, blank=True, null=True)
    password = models.CharField(max_length=50)
    isadmin = models.BooleanField(db_column='isAdmin', default=False)
    avatar = models.ImageField(
        upload_to='home/static/uploads/', default='home/static/uploads/default.png')
    gender = models.CharField(max_length=6, choices=[('male', 'Nam'), ('female', 'Nữ'), ('null', 'Chưa cập nhật')],
                              default='null')
    birthday = models.DateField(null=True, blank=True)
    bio = models.TextField(blank=True, null=True)
    createdat = models.DateTimeField(
        db_column='createdAt', default=datetime.now())
    updatedat = models.DateTimeField(db_column='updatedAt', auto_now=True)

    def __str__(self):
        return self.username.format()


class Collection(models.Model):
    name = models.CharField(max_length=100, blank=True, null=False)
    createdat = models.DateTimeField(
        db_column='createdAt', default=datetime.now())
    updatedat = models.DateTimeField(db_column='updatedAt', auto_now=True)

    def __str__(self):
        return self.name.format()


class Blog(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=100, blank=True, null=False)
    content = RichTextField(blank=True, null=False)
    userid = models.ForeignKey(
        User, models.DO_NOTHING, db_column='userId', related_name='blogs')
    status = models.BooleanField(default=False)
    image = models.ImageField(upload_to='home/static/uploads/')
    collectionId = models.ManyToManyField(
        Collection, db_column='collectionId', related_name='blogs')
    view = models.IntegerField(default=0)
    createdat = models.DateTimeField(
        db_column='createdAt', default=datetime.now())
    updatedat = models.DateTimeField(db_column='updatedAt', auto_now=True)

    def __str__(self):
        return self.title.format()


class Comment(models.Model):
    iduser = models.ForeignKey(User, models.DO_NOTHING, db_column='idUser')
    idblog = models.ForeignKey(Blog, models.DO_NOTHING, db_column='idBlog')
    content = models.TextField(blank=True, null=False)
    createdat = models.DateTimeField(
        db_column='createdAt', default=datetime.now())
    updatedat = models.DateTimeField(db_column='updatedAt', auto_now=True)

    def __str__(self):
        return self.content.format()


class Reaction(models.Model):
    iduser = models.ForeignKey(User, models.DO_NOTHING, db_column='idUser')
    idblog = models.ForeignKey(Blog, models.DO_NOTHING, db_column='idBlog')
    reaction = models.CharField(max_length=10,
                                choices=[('like', 'Like'),
                                         ('dislike', 'Dislike')],
                                blank=True,
                                null=True)
    createdat = models.DateTimeField(
        db_column='createdAt', default=datetime.now())
    updatedat = models.DateTimeField(db_column='updatedAt', auto_now=True)

    class Meta:
        unique_together = (('iduser', 'idblog'),)
