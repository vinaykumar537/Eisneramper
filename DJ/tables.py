import django_tables2 as tables
from  DJ.models import *
from django_tables2.utils import A 



class CustomTemplateColumn(tables.TemplateColumn):
   def render(self, record, table, value, bound_column, **kwargs):
        if record.status == "done":
            return 'Done'
        
        return super(CustomTemplateColumn, self).render(record, table, value, bound_column, **kwargs)

class CustomTemplateColumnEdit(tables.TemplateColumn):
   def render(self, record, table, value, bound_column, **kwargs):
          
        return super(CustomTemplateColumnEdit, self).render(record, table, value, bound_column, **kwargs)


class BusinessTable(tables.Table):
    T1 = '<a class="btn btn-primary"  href="edit/businessactivity/{{record.id}}/">Edit</a>'
    T2 = '<a class="btn btn-info" href="edit/{{ record.id }}">Add</a>'
    Business= CustomTemplateColumnEdit(T1)
    Regulation   = CustomTemplateColumn(T2)
    businessactivity = tables.Column(verbose_name= 'Business Activity' )
    class Meta:
        model = Business
        fields =['businessactivity']    
        template_name = 'django_tables2/semantic.html'

class PersonTable(tables.Table):
    # T1 = '<a href="edit/regulation/{{record.id}}/">EDIT</a>'
    # T2 = '<a href="edit/{{ record.id }}">ADD</a>'
    T1='<a class="btn btn-primary"   href="edit/regulation/{{record.id}}/" >Edit</a>'
    T2='<a class="btn btn-info"   href="edit/{{ record.id }}" >Add</a>'
    Regulation = CustomTemplateColumnEdit(T1)
    Policy   = CustomTemplateColumn(T2)
    businessdefinition_a = tables.Column(verbose_name= 'Business Definition' )
    regulation = tables.Column(verbose_name= 'Regulation' )
    # category = tables.Column(verbose_name='Category')
    class Meta:
        model = BAReg
        fields =['businessdefinition_a', 'regulation']
        template_name = 'django_tables2/semantic.html'

class ControlTable(tables.Table):
    T1 = '<a class="btn btn-primary"  href="edit/process/{{record.id}}/">Edit</a>'
    T2 = '<a class="btn btn-info" href="/add_control/{{ record.id }}">Add</a>'
    Policy = CustomTemplateColumnEdit(T1)
    Control   = CustomTemplateColumn(T2)
    businessdefinition_a = tables.Column(verbose_name= 'Business Definiton' )
    regulation = tables.Column(verbose_name= 'Regulation' )
    process = tables.Column(verbose_name= 'Policy' )
    # category = tables.Column(verbose_name='Category')
    class Meta:
        model = ProcessReg
        fields =['businessdefinition_a','regulation', 'process']
        template_name = 'django_tables2/semantic.html'


class RiskTable(tables.Table):
    T1 = '<a class="btn btn-primary" href="edit/control/{{record.id}}/">Edit</a>'
    T2 = '<a  class="btn btn-info" href="/add_risk/{{ record.id }}">Add</a>'
    Control = CustomTemplateColumnEdit(T1)
    Risk   = CustomTemplateColumn(T2)
    businessdefinition_a = tables.Column(verbose_name= 'Business Definiton' )
    regulation = tables.Column(verbose_name= 'Regulation' )
    process = tables.Column(verbose_name= 'Policy' )
    controlarea = tables.Column(verbose_name= 'Control' )
    # category = tables.Column(verbose_name='Category')
    class Meta:
        model = ControlReg
        fields =['businessdefinition_a','regulation', 'process', 'controlarea']
        template_name = 'django_tables2/semantic.html'

class FinalTable(tables.Table):
    T1 = '<a class="btn btn-primary" href="edit/risk/{{record.id}}/">Edit</a>'
    T2= '<a class="btn btn-danger" href="delete_allmapping/{{record.id}}/">Delete</a>'
    Risk = CustomTemplateColumnEdit(T1)
    Delete = CustomTemplateColumnEdit(T2)
    businessdefinition_a = tables.Column(verbose_name= 'Business Definiton' )
    regulation = tables.Column(verbose_name= 'Regulation' )
    process = tables.Column(verbose_name= 'Policy' )
    controlarea = tables.Column(verbose_name= 'Control' )
    risk = tables.Column(verbose_name= 'Risk' )
    # category = tables.Column(verbose_name='Category')
    class Meta:
           model = RiskReg
           fields = ['businessdefinition_a', 'regulation', 'process', 'controlarea', 'risk']
           template_name = 'django_tables2/bootstrap-responsive.html'

class FinalviewTable(tables.Table):
    businessdefinition_a = tables.Column(verbose_name= 'Business Definiton' )
    regulation = tables.Column(verbose_name= 'Regulation' )
    process = tables.Column(verbose_name= 'Policy' )
    controlarea = tables.Column(verbose_name= 'Control' )
    risk = tables.Column(verbose_name= 'Risk' )
    category = tables.Column(verbose_name='Category')
    class Meta:
           model = RiskReg
           fields = [ 'category','businessdefinition_a', 'regulation', 'process', 'controlarea', 'risk']
           template_name = 'django_tables2/semantic.html'

class GroupTable(tables.Table):
    groupname = tables.Column(verbose_name= 'Group Name' )
    BusinessActivity = tables.Column(verbose_name= 'Business Activity' )
    class Meta:
           model = BusinessGroup
           fields = [ 'groupname', 'BusinessActivity']
           template_name = 'django_tables2/semantic.html'
    