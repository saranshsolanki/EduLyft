from django import forms
from django.db import models
from django.forms import DateInput
from django.forms.fields import DateField, ChoiceField
from django.forms.models import ModelForm, modelformset_factory
from django.forms.widgets import RadioSelect, TextInput
import os


# StudentAnswers.objects.filter(student_id__exact = 1, question__test__exact = 10)
# Create your models here.
class SubjectsList(models.Model):
    name = models.CharField(max_length = 200, unique = True)
    
    
    def __unicode__(self): # Python 3: def __str__(self):
        return unicode(self.name) or u''

class ChaptersList(models.Model):
    name = models.CharField(max_length = 200, unique = True)
    subject = models.ForeignKey(SubjectsList)
    
    def __unicode__(self): # Python 3: def __str__(self):
        return self.name
    
class Tests(models.Model):
    name = models.CharField(max_length = 200, unique = True)
    instructions = models.TextField(blank = True)
    test_date = models.DateField(auto_now=False, auto_now_add=False)
    no_of_questions = models.IntegerField(max_length = 5)
    is_answers_filled = models.BooleanField(default=False)
    
    def __unicode__(self): # Python 3: def __str__(self):
        return self.name
    
class DateInput(forms.DateInput):
    input_type = 'date'

class TestsForm(ModelForm):
    class Meta:
        model = Tests
        exclude = ('is_answers_filled',)
        widgets = {
            'test_date': DateInput()
        }
        field_args = {
        "name" : {
            "error_messages" : {
                "required" : "Please enter a test name.",
                "unique": "This Test Name already exists."
            }           
        },
        "test_date" : {
            "error_messages" : {
                "required" : "Please enter a test date."
            }           
        }
    }

    
class Questions(models.Model):
    ANSWER_CHOICES = (('A','A'),('B', 'B'), ('C','C'), ('D','D'))
    LOD_CHOICES = ((1,'Easy'),(2,'Medium'),(3,'Hard'))
    TYPE_CHOICES = ((1,'Single Correct'),(2,'Multi Correct'),(3,'Integer'))   
    test = models.ForeignKey(Tests)
    question_no = models.IntegerField(max_length=5)
    subject = models.ForeignKey(SubjectsList)
    chapter = models.ForeignKey(ChaptersList)
    lod = models.IntegerField(max_length=100, choices=LOD_CHOICES)
    type = models.IntegerField(max_length=100, choices=TYPE_CHOICES)
    answer = models.CharField(max_length=100)
    correct_score = models.IntegerField(max_length=5, default = 3)
    wrong_score = models.IntegerField(max_length=5, default = -1)
    
    def __unicode__(self): 
        return unicode(self.question_no) or u''
    
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
    
class QuestionsForm(ModelForm):
    #ANSWER_CHOICES = (('A','A'),('B', 'B'), ('C','C'), ('D','D'))  
    subject = InlineModelChoiceField(queryset = SubjectsList.objects.all(), 
                                     widget=forms.TextInput(attrs={'class':'subject_class'}))
    chapter = InlineModelChoiceField(queryset = ChaptersList.objects.all(), 
                                     widget=forms.TextInput(attrs={'class':'chapter_class'}))
    #answer = forms.ChoiceField(widget=RadioSelect(), choices = ANSWER_CHOICES)
        
    class Meta:
        #ANSWER_CHOICES = ('A', 'B', 'C', 'D')
        model = Questions
        chapter = forms.ModelChoiceField(queryset = ChaptersList.objects.all())
        exclude = ('test',)
        widgets = {
        'question_no':TextInput(attrs={'size': '5'}),
        'correct_score':TextInput(attrs={'size': '5'}),
        'wrong_score':TextInput(attrs={'size': '5'})
        }
        field_args = {
        "question_no" : {
            "error_messages" : {
                "required" : "Please enter a question number.",
                "unique": "This Test Name already exists."
            }           
        },
        "answer" : {
            "error_messages" : {
                "required" : "Please enter an answer for this question."
                }           
            }
        }

class TestPerformance(models.Model):
    student = models.ForeignKey('auth.User')
    test = models.ForeignKey(Tests)
    physics_score = models.IntegerField(max_length=5)
    chemistry_score = models.IntegerField(max_length=5)
    math_score = models.IntegerField(max_length=5)
    overall_score = models.IntegerField(max_length=5)
    insti_rank = models.IntegerField(max_length=10)
    phy_insti_rank = models.IntegerField(max_length=10)
    chem_insti_rank = models.IntegerField(max_length=10)
    math_insti_rank = models.IntegerField(max_length=10)
    
IMPORT_FILE_TYPES = ['.xls', ]

class XlsInputForm(forms.Form):
    input_excel = forms.FileField(label= u"Upload the Excel file to import to the system.")

    def clean(self):
        input_excel = self.cleaned_data['input_excel']
        extension = os.path.splitext( input_excel.name )[1]
        print extension
        if not (extension in IMPORT_FILE_TYPES):
            raise forms.ValidationError( u'%s is not a valid excel file. Please make sure your input file is an excel file (Excel 2007 is NOT supported.' % extension )
        else:
            return input_excel
