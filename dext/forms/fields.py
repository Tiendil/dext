# -*- coding: utf-8 -*-
import functools

from django import forms

def strip_on_clean(cls):

    old_init = cls.__init__
    old_clean = cls.clean
    
    @functools.wraps(old_init)
    def new_init(self, strip=' ', *args, **kwargs):
        if not strip:
            strip = ''
        self._strip = strip
        old_init(self, *args, **kwargs)

    @functools.wraps(old_clean)
    def new_clean(self, value):
        return old_clean(self, value.strip(self._strip) if value else value)

    cls.__init__ = new_init
    cls.clean = new_clean

    return cls

def pgf(cls):
    old_init = cls.__init__
    
    @functools.wraps(old_init)
    def new_init(self, pgf={}, *args, **kwargs):
        self.pgf = pgf
        old_init(self, *args, **kwargs)

    cls.__init__ = new_init

    return cls



@strip_on_clean
@pgf
class CharField(forms.CharField): pass

class TextField(CharField):
    widget = forms.Textarea

@strip_on_clean
@pgf
class EmailField(forms.EmailField): pass

@strip_on_clean
@pgf
class RegexField(forms.RegexField): pass

@strip_on_clean
@pgf
class IntegerField(forms.IntegerField): pass

@pgf
class ChoiceField(forms.ChoiceField): pass

class PasswordField(RegexField): 

    REGEX = r'[a-zA-Z0-9!@#$%^&*()-_=+]+'
    MIN_LENGTH = 6
    MAX_LENGTH = 50

    def __init__(self, *args, **kwargs):
        super(PasswordField, self).__init__(regex=self.REGEX, 
                                            min_length=self.MIN_LENGTH, 
                                            max_length=self.MAX_LENGTH,
                                            widget=forms.PasswordInput,
                                            *args, **kwargs)


class HiddenCharField(CharField): 

    def __init__(self, *args, **kwargs):
        super(HiddenCharField, self).__init__(widget=forms.HiddenInput, *args, **kwargs)

class HiddenIntegerField(IntegerField): 

    def __init__(self, *args, **kwargs):
        super(HiddenIntegerField, self).__init__(widget=forms.HiddenInput, *args, **kwargs)