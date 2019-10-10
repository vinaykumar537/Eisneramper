from django import forms
from django.forms import ModelForm
from .models import *
from django.forms import formset_factory
from .fields import *


class RegulationForm(forms.Form):


    regulations=Regulations.objects.values_list('regulation','regulation')
    choices = (
        regulations
    )
    Regulations = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple,choices=choices)

class BusinessForm(forms.Form):

   options = [('New York', 'New York'), ('Boston', 'Boston'),('Alaska','Alaska')]

   Jurisdiction = forms.ChoiceField(widget=forms.Select(attrs={'class':'drop'}), choices=options)
   regulations=BusinessActivity.objects.only("businessdefinition_a")
   choices = BusinessActivity.objects.only("businessdefinition_a","businessdefinition_q")
   Business_Activities = GroupedModelChoiceField(
           widget=forms.CheckboxSelectMultiple(attrs={'class':'b_choice'}),
           choices_groupby='businessdefinition_q',
           queryset=choices)

    
  

class CustomBusinessForm(forms.Form):
    class Meta:
        model = BusinessActivity

    businessdefinition_q = forms.CharField(
        label='Business Definition Question',
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Business Definition Question'
        })
    )
    businessdefinition_a = forms.CharField(
        label='Business Definition Answer',
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Business Definition Answer'
        })
    )
    jurisdiction = forms.CharField(
        label='Jurisdiction',
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Enter Jurisdiction'
        })
    )
    
CustomBusinessFormSet = formset_factory(CustomBusinessForm)

class ProcessForm(forms.Form):
    title = forms.CharField(
        label='Policy Title',
        widget=forms.Textarea(attrs={'required': 'true','rows': 4, 'cols': 100,
            'class': 'form-control',
            'placeholder': 'Enter Policy Title here',
            'required':'This Field is Required',
            
        })
    )
    description = forms.CharField(
        label='Process Description',
        widget=forms.Textarea(attrs={'required': 'true','rows': 4, 'cols': 100,
            'class': 'form-control',
            'placeholder': 'Enter Policy Description',
            'required':'This Field is Required'
        })
    )
    
ProcessFormSet = formset_factory(ProcessForm)

class ControlForm(forms.Form):
    control = forms.CharField(
        label='Control Title',
        widget=forms.Textarea(attrs={'required': 'true','rows': 4, 'cols': 100,
            'class': 'form-control',
            'placeholder': 'Enter Control Area',
            'required':'This Field is Required'
        })
    )
    description = forms.CharField(
        label='Control Description',
        widget=forms.Textarea(attrs={'required': 'true','rows': 4, 'cols': 100,
            'class': 'form-control',
            'placeholder': 'Enter Control Description',
            'required':'This Field is Required'
        })
    )
    content = forms.CharField(
        label='Control Content',
        widget=forms.Textarea(attrs={'required': 'true','rows': 4, 'cols': 100,
            'class': 'form-control',
            'placeholder': 'Enter Control Objective',
            'required':'This Field is Required'
        })
    )
ControlFormSet = formset_factory(ControlForm)
     
class RiskForm(forms.Form):
    OPTIONS = [
          ('Low', 'Low'),
          ('Medium', 'Medium'),
          ('High','High')
    ]

    risk = forms.CharField(label='Select Level of Risk', widget=forms.RadioSelect(choices=OPTIONS))
    comment = forms.CharField(
        label='Risk Title',
        widget=forms.Textarea(attrs={
            'class': 'form-control','rows': 4, 'cols': 100,
            'placeholder': 'Enter Risk Comment',
            'required':'This Field is Required'
        })        
    )
    description = forms.CharField(
        label='Risk Description',
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Enter Risk Description',
            'required':'This Field is Required'
        })
       
    )




RiskFormSet = formset_factory(RiskForm)


class EditRegulationForm(forms.Form):
    regulations=Regulations.objects.values_list('regulation','regulation')
    choices = (
        regulations
    )
    Regulation = forms.CharField(label='Select Regulation to be updated', widget=forms.RadioSelect(choices=choices))


class EditBusinessForm(forms.Form):
     options = [('New York', 'New York'), ('Boston', 'Boston'),('Alaska','Alaska')]
     Jurisdiction = forms.ChoiceField(widget=forms.Select(attrs={'class':'drop'}), choices=options)
     choices = BusinessActivity.objects.only("businessdefinition_a","businessdefinition_q")
     Business_Activities = GroupedModelChoiceField(
          widget=forms.RadioSelect(attrs={'class':'b_choice'}),
          choices_groupby='businessdefinition_q',
          queryset=choices)



