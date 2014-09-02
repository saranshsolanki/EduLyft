from django import forms
from django.contrib.auth.models import User
from django.db import models
from django.forms.models import ModelForm, modelformset_factory
from django.forms.widgets import RadioSelect, TextInput
from django.utils import importlib
import os

from Students.models import StudentAnswers


#from tests.models import Tests
tests_app = models.get_app("tests")

models_tests = importlib.import_module(tests_app.__name__[:-6] + "models") 

class InlineModelChoiceField(forms.ModelChoiceField):
    def __init__(self, *args, **kwargs):
        kwargs['widget'] = kwargs.pop('widget', forms.widgets.TextInput)
        super(InlineModelChoiceField, self).__init__(*args, **kwargs)

    def clean(self, value):
        if not value and not self.required:
            return None
        try:
            return self.queryset.filter(name=value).get()
        except self.queryset.model.DoesNotExist:
            raise forms.ValidationError("Please enter a valid %s." % (self.queryset.model._meta.verbose_name,))

class InlineModelChoiceField2(forms.ModelChoiceField):
    def __init__(self, *args, **kwargs):
        kwargs['widget'] = kwargs.pop('widget', forms.widgets.TextInput)
        super(InlineModelChoiceField2, self).__init__(*args, **kwargs)

    def clean(self, value):
        if not value and not self.required:
            return None
        try:
            return self.queryset.filter(username=value).get()
        except self.queryset.model.DoesNotExist:
            raise forms.ValidationError("Please enter a valid %s." % (self.queryset.model._meta.verbose_name,))
      

class LoginForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(attrs={'placeholder':'Username'}),required=True)
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder':'Password'}),required=True)

class TestAndStudentNameForm(forms.Form):
    
    testname = InlineModelChoiceField(queryset = models_tests.Tests.objects.all(), 
                                     widget=forms.TextInput(attrs={'class':'subject_class'}))
    studentname = InlineModelChoiceField2(queryset = User.objects.all(), 
                                     widget=forms.TextInput(attrs={'class':'chapter_class'}))
    input_excel = forms.FileField(label = u"Student response Excel file.")
    
    def clean(self):
        IMPORT_FILE_TYPES = ['.xls', ]
        
        cleaned_data = super(TestAndStudentNameForm, self).clean()
        #input_excel = cleaned_data.get('input_excel')
        input_excel = self.cleaned_data['input_excel']
        extension = os.path.splitext( input_excel.name )[1]
        print extension
        if not (extension in IMPORT_FILE_TYPES):
            raise forms.ValidationError( u'%s is not a valid excel file. Please make sure your input file is an excel file (Excel 2007 is NOT supported.' % extension )
        else:
            return input_excel
    
class StudentAnswersForm(forms.Form):
    #ANSWER_CHOICES = (('A','A'),('B', 'B'), ('C','C'), ('D','D'))
    question_no = forms.IntegerField(required=True)  
    attempt_ans = forms.CharField(max_length=5, required=False)
    
    def __init__(self, *arg, **kwarg):
        super(StudentAnswersForm, self).__init__(*arg, **kwarg)
        self.empty_permitted = False
           
    