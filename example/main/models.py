from django.db import models
import uuid
import names
import random


class Person(models.Model):
    ''' Instance of this model represents a human being '''
    uuid = models.UUIDField(default = uuid.uuid4, editable=False)
    last_name = models.CharField(max_length=100, null=True)
    first_name = models.CharField(max_length=100, null=True)
    middle_name = models.CharField(max_length=100, null=True, blank=True)
    salary = models.FloatField(null=True)
    adjectives = models.ManyToManyField('PersonAdjective')

    @property
    def full_name(self):
        mn = '' if self.middle_name==None else self.middle_name
        return f'{self.first_name} {mn} {self.last_name}'

    @classmethod
    def generate_random_people(cls, wipe_table=False, n=10):
        ''' classmethod to generate random people by calling generate_random_person module '''
        if wipe_table==True:
            cls.objects.all().delete()
        for i in range(n):
            cls.generate_random_person()

    @classmethod
    def generate_random_person(cls, gender=None):
        ''' classmethod to generate a random person '''
        if gender!=None:
            assert gender in ['male', 'female'], 'gender must be either "male" or "female"'
        else:
            gender = random.choice(['female', 'male'])
        name = names.get_full_name(gender=gender)
        fn = name.split(' ')[0]
        mn = names.get_first_name(gender=gender)
        ln = name.split(' ')[1]
        obj, c = cls.objects.get_or_create(last_name=ln, first_name=fn, middle_name=mn)
        return obj

    def get_salary(self):
        ''' Method to get a random salary if none '''
        if self.salary: return
        self.salary = round(random.uniform(15_000.00, 200_000.00), 2)

    def get_adjectives(self):
        ''' Method to randomly assign person adjectives '''
        self.adjectives.clear()
        self.adjectives.add(*PersonAdjective.objects.order_by('?')[:3])

    def save(self, *args, **kwargs):
        self.get_salary()
        super().save(*args, **kwargs)
        self.get_adjectives()

    def __str__(self):
        return self.full_name


class PersonAdjective(models.Model):
    ''' Instance of this class represents an adjective that could describe a person '''
    DEFAULTS = ['nice', 'mean','funny', 'serious', 'tall', 'short']

    word = models.CharField(max_length=100, unique=True)
    definition = models.CharField(max_length=500, null=True, blank=True)

    @classmethod
    def create_defaults(cls):
        for word in cls.DEFAULTS:
            cls.objects.get_or_create(word=word)

    def get_absolute_url(self):
        return '#'

    def __str__(self):
        return f'{self.word}'