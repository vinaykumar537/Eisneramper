from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from . models import *
from django.db import connection
from . forms import *
from . tables import *
from django_tables2 import RequestConfig
from django.http import HttpResponseRedirect
from django.template import loader
from django.shortcuts import render
from django.contrib.auth import authenticate, login as user_login
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout as logout_required
import pandas as pd
import numpy as np
pd.options.mode.chained_assignment = None
import json

from django.contrib import messages

# Create your views here.

## To view Login page 
def home(request):
    return render(request,'login.html')

""" Login Method:
Input: Uername & Password """
def login(request):
    if request.method == 'POST':
        username = request.POST['uname'] # Extracting username from login form
        password = request.POST['pwd'] # Extracting password from login form
        user = authenticate(username=username, password=password) # validating the user
        if user is not None:
           user_login(request, user) # Make user login, if validation got success
           return redirect('homepage') 
        else:
            messages.error(request, "Incorrect Username or Password ")
            return redirect('home') 
    else:
        return render(request, 'login.html')

""" Logout Method:
Input : requested user """
def logout(request):
   logout_required(request) # alias name for logout to avaoid recurssion
   return redirect('home')

""" Home page:
Input : HTTP Request """
@login_required
def homepage(request):
    return render(request,'Homepage.html/')


@login_required
def index(request):
   item  = Regulations.objects.all()
   return render(request, 'Reg.html/', {'items':item})


@login_required
def countries_view(request):
    balist=request.session['balist']
    user=request.user
    for ba in balist:
         count=Business.objects.filter(businessactivity=ba, user=user).count()
         if(count<1):
           Business(businessactivity=ba, user=user).save()
    return redirect('firstpage')

""" Method for selection of regulations and grouping
Input : Regulation form, Where user allows to select multiple regulation
Output: Corresponding mapping result, should be saved in BAReg Table """
@login_required
def bagroupall(request):
   heading_message = 'Group Regulations Management'
   user=request.user
   items  = Regulations.objects.all()
   name=request.session['groupname']
   if request.method == 'POST':
       form = RegulationForm(request.POST or None)
       if form.is_valid():
           regulations = form.cleaned_data.get('Regulations') # Extracting the Regulation from Regulation form
           request.session['reg']=regulations  # Storing the regulations to current session
           if regulations: # Storing regualtion & BA Group Mapping in BAReg
                   for regulation in regulations:
                       count=BAReg.objects.filter(regulation=regulation, businessdefinition_a ='Group - '+name , user=user,category=name).count()
                       if (count<1):
                          BAReg(regulation=regulation, businessdefinition_a ='Group - '+name, user=user,category=name).save()

           return redirect('secondpage')
   else:
           form = RegulationForm(request.GET or None)
   return render(request,'Reg.html/', { 'form' : form,'heading' : heading_message, 'items':items, 'user': user })

""" Method for selection of Business Activities
Input : Business Form, Which allow user to slect multiple business activities."""
@login_required
def selectbusiness(request):
   heading_message = 'Business Management'
   user=request.user
   baas = []
   item = BusinessActivity.objects.all()
   groups = BusinessGroup.objects.filter(user=request.user).all()
   request.session['title']=[]  #making new session which holds current process data
   request.session['control']=[] #making new session which holds current control data
   request.session['risk']=[] #making new session which holds current risk data
   if request.method == 'POST':
       # formset=CustomBusinessFormSet(request.POST or None)
       form=BusinessForm(request.POST or None)
       if  form.is_valid():
           businessactivitites=form.cleaned_data.get('Business_Activities') # Extracting the selected BA's, from form
           jurisdiction = form.cleaned_data.get('Jurisdiction')
             # Extracting the Jurisdiction, from dropdown
           for activity in businessactivitites:
               baas.append(str(activity.businessdefinition_q)+str("/")+str(activity.businessdefinition_a)+str("/")+str(jurisdiction))
           group=request.POST.get('groupall')
           groupName=request.POST.get('groupname')
           request.session['balist']=baas
           request.session['group']=group
           request.session['groupname']=groupName
           if group == 'yes':
                for ba in baas:
                    c = BusinessGroup.objects.filter(groupname=groupName, BusinessActivity=ba, user=user).count()
                    if (c<1):
                        BusinessGroup(groupname=groupName, BusinessActivity=ba, user=user).save()
                return redirect('bagroupall')
           else:
              return redirect('countries_view')
       else:
           messages.error(request, "Atleast one field is required.") # Form validation
           return redirect('selectbusiness')
   else:
          form=BusinessForm(request.GET or None)
          return render(request,'BA.html/', { 'form' : form,
          'heading' : heading_message,
          'items' : item,
          'user' : user,
          'groups' : groups
          })


def convert(parent,string,color):
        res ={
                'name': string,
                'parent':parent,
                'children':[],
                'level':color   
            }
        return res



@login_required
def secondpage(request):
        # ba = request.session.get('ba')
        # balist = request.session.get('balist')
        groups=[]
        individuals=[]
        grouplist=BAReg.objects.filter(user=request.user).exclude(category='Individual').values_list('category')
        individualist=BAReg.objects.filter(user=request.user,category='Individual').values_list('businessdefinition_a')
        # individualist=BAReg.objects.filter(user=request.user).exclude(category='Individual').values_list('businessdefinition_a')
        grouplist=list(grouplist)
        individualist=list(individualist)
        for group in grouplist:
            if group not in groups:
                groups.append(group[0])
        for single in individualist:
            individuals.append(single[0])
        groups=list(set(groups))
        individuals=list(set(individuals))
        group=request.session['group']        
        current_user=request.user
        count =BAReg.objects.filter(user=current_user).count()
        done_count=BAReg.objects.filter(user=current_user, status='done').count()
        if count == done_count:
           button_enable = True
        else:
           button_enable = False
        table = PersonTable(BAReg.objects.filter(user=current_user))
        RequestConfig(request).configure(table)
        group_chart_data_list=[]#to store json data for each business activity
        single_chart_data_list=[]#to store json data for each business activity

        single_df=BAReg.objects.filter(user=request.user,category='Individual').values_list('businessdefinition_a','regulation')
        if single_df:
            df2=pd.DataFrame(list(single_df),columns=['Business_Definition','Regulation'])
            # df2=df.Regulation.apply(pd.Series).merge(df, right_index = True, left_index = True).drop(["Regulation"], axis = 1).melt(id_vars = ['Business_Definition'], value_name = "Regulation").drop("variable", axis = 1).dropna()
            n=len(individuals)#to store number of business activities for current user
            #parent,child mapping single level
            for l in range(0,n):
                df3=df2[df2['Business_Definition']==individuals[l]]
                # print(df3)
                df3.reset_index(inplace = True, drop = True)
                b_color="#4d88ff" 
                final_tree=convert("Null",df3.loc[0,"Business_Definition"],b_color)
                Reg_Tree=df3["Regulation"].unique().tolist()
                re_color="burlywood"
                for i in range(0,len(Reg_Tree)):
                    element=convert(df3.loc[0,"Business_Definition"],Reg_Tree[i],re_color)
                    final_tree['children'].append(element)
                chart_data=json.dumps(final_tree,indent=2)
                single_chart_data_list.append(chart_data)
            
            individuals.reverse()
            single_chart_data_list.reverse()
        # name=request.session['groupname']

        group_df=BAReg.objects.filter(user=request.user).exclude(category='Individual').values_list('category','regulation')
        if group_df:
            df2=pd.DataFrame(list(group_df),columns=['Business_Definition','Regulation'])
            # df2=df.Regulation.apply(pd.Series).merge(df, right_index = True, left_index = True).drop(["Regulation"], axis = 1).melt(id_vars = ['Business_Definition'], value_name = "Regulation").drop("variable", axis = 1).dropna()
            n=len(groups)#to store number of business activities for current user
            #parent,child mapping single level
            for l in range(0,n):
                df3=df2[df2['Business_Definition']==groups[l]]
                # print(df3)
                df3.reset_index(inplace = True, drop = True)
                b_color="#4d88ff" 
                final_tree=convert("Null",df3.loc[0,"Business_Definition"],b_color)
                Reg_Tree=df3["Regulation"].unique().tolist()
                re_color="burlywood"
                for i in range(0,len(Reg_Tree)):
                    element=convert(df3.loc[0,"Business_Definition"],Reg_Tree[i],re_color)
                    final_tree['children'].append(element)
                chart_data=json.dumps(final_tree,indent=2)
                group_chart_data_list.append(chart_data)
            groups.reverse()
            group_chart_data_list.reverse()
        context = {'table': table, 'flag' : button_enable,'group_data':group_chart_data_list, 'single_data': single_chart_data_list,'individuals':individuals, 'groups':groups,  'user' : current_user}
        return render(request,'Process_1.html/',context)

""" Methods to display the ProcessReg Mapping
Input : Process Reg Table(Model)
Output: Control Table """
@login_required
def thirdpage(request):
        current_user=request.user
        count =ProcessReg.objects.filter(user=current_user).count() # To Enable, Disable Next Button
        done_count=ProcessReg.objects.filter(user=current_user, status='done').count()
        if count == done_count: 
           button_enable = True
        else:
           button_enable = False
        table = ControlTable(ProcessReg.objects.filter(user=current_user))  # Configuring the  Control Table with Process Reg Data
        RequestConfig(request).configure(table)
        context = {'table': table, 'flag' : button_enable}
        return render(request,'Process_2.html/',context)

""" Method to display ControlReg Mapping
Input: Control Reg Table (Model)
Output:Risk Table """
@login_required
def fourthpage(request):
        current_user=request.user
        count =ControlReg.objects.filter(user=current_user).count()  # To Enable, Disable Next Button
        done_count=ControlReg.objects.filter(user=current_user, status='done').count()
        if count == done_count:
           button_enable = True
        else:
           button_enable = False
        table = RiskTable(ControlReg.objects.filter(user=current_user))  # Configuring the Risk Table with Control Reg Data
        RequestConfig(request).configure(table)
        context = {'table': table, 'flag' : button_enable}
        return render(request,'fourthpage.html/',context)

""" Method to add Process's
Input: Process Formset
Output: Storing mapping in Process Reg Table """
@login_required
def edit_item(request, pk):
    item = get_object_or_404(BAReg, id=pk) # Adding process based on id
    if request.method == 'POST':
        formset = ProcessFormSet(request.POST)  # Process Form Set
        if formset.is_valid():
            BAReg.objects.filter(pk=pk).update(status='done')
            user=request.user
            for form in formset: # Extracting the Processes from Process Form set
                 title= form.cleaned_data.get('title')
                 description = form.cleaned_data.get('description')
                 Policy(policy=title, description=description, user=user).save()
                 ProcessReg(regulation=item.regulation, businessdefinition_a = item.businessdefinition_a, businessdefinition_q = item.businessdefinition_q, jurisdiction=item.jurisdiction, 
                 process=title, description=description, user=user,category=item.category).save() # Saving the Process's in Process Reg Mapping Table
          
            return redirect('secondpage')
    else:
        formset = ProcessFormSet(request.GET or None)
    return render(request, 'Process_2.html', {
        'formset': formset,
    })
        
""" Method to select control
Input : Control Formset
Output: Storing Mapping in Control Reg Table """
@login_required  
def select_control(request, pk):
    item = get_object_or_404(ProcessReg, id=pk)
    heading_message = 'Control Management'
    user=request.user
    if request.method == 'POST':
        formset = ControlFormSet(request.POST)   # Displaying the Control Form Set
       
        if formset.is_valid():
            ProcessReg.objects.filter(pk=pk).update(status='done') # Updating the status as done
            user=request.user
            for form in formset:
                 control= form.cleaned_data.get('control')
                 description = form.cleaned_data.get('description')
                 content = form.cleaned_data.get('content')
                #  Controls(control=control, description=description, content=content, user=user).save()
                 ControlReg(regulation=item.regulation, businessdefinition_a = item.businessdefinition_a, businessdefinition_q = item.businessdefinition_q, jurisdiction=item.jurisdiction, 
                 process=item.process, description=item.description, controlarea=control, controldescription=description, controlobjective=content, user=user,category=item.category).save() # Saving the data in Control Reg Model
            return redirect('selectcontrol')
    else:
        formset = ControlFormSet(request.GET or None)

    return render(request, 'control_2.html', {
        'formset': formset,
        'heading': heading_message,
        'user' : user
    })

""" Method to display the Process Reg Table
Input : Process Reg Table (Model)
Output: Control Table """
@login_required
def selectcontrol(request):
        group=request.session['group']
        current_user=request.user
        count =ProcessReg.objects.filter(user=current_user).count()    # To Enable, Disable Next Button
        done_count=ProcessReg.objects.filter(user=current_user, status='done').count()
        if count == done_count:
           button_enable = True
        else:
           button_enable = False
        table = ControlTable(ProcessReg.objects.filter(user=current_user))  # Configuring the Control Table with Process Reg Data
        RequestConfig(request).configure(table)
        groups=[]
        individuals=[]
        grouplist=ProcessReg.objects.filter(user=request.user).exclude(category='Individual').values_list('category')
        individualist=ProcessReg.objects.filter(user=request.user,category='Individual').values_list('businessdefinition_a')
        grouplist=list(grouplist)
        individualist=list(individualist)
        for group in grouplist:
            if group not in groups:
                groups.append(group[0])
        for single in individualist:
            individuals.append(single[0])
        groups=list(set(groups))
        individuals=list(set(individuals))
        single_chart_data_list=[] #to store json data for each business activity
        group_chart_data_list=[] #to store json data for each business activity
        #graph for group of business activities
        # name=request.session['groupname']
        group_df=ProcessReg.objects.filter(user=request.user).exclude(category='Individual').values_list('category','regulation','process')
        
        if group_df:
            df2=pd.DataFrame(list(group_df),columns=['Business_Definition','Regulation','Policy'])
            # df2=df.Policy.apply(pd.Series).merge(df, right_index = True, left_index = True).drop(["Policy"], axis = 1).melt(id_vars = ['Business_Definition','Regulation'], value_name = "Policy").drop("variable", axis = 1).dropna()
            #parent,child mapping
            for l in range(0,len(groups)):
                df3=df2[df2['Business_Definition']==groups[l]]
                # print(df3)
                df3.reset_index(inplace = True, drop = True)
                b_color="#4d88ff"
                final_tree=convert("Null",df3.loc[0,"Business_Definition"],b_color)
                # print(final_tree)
                Reg_Tree=df3["Regulation"].unique().tolist()
                # print(Reg_Tree)
                re_color="burlywood"
                for i in range(0,len(Reg_Tree)):
                    element=convert(df3.loc[0,"Business_Definition"],Reg_Tree[i],re_color)
                    final_tree['children'].append(element)
                temp=final_tree['children'].copy()
                p_color="#99ff99"
                for i in range(0,len(temp)):
                    temp_sub=temp[i].copy()
                    df_sub=df3[df3['Regulation']==temp_sub['name']]
                    df_sub.reset_index(drop=True,inplace=True)
                    policy_tree=df_sub["Policy"].unique().tolist()
                    for j in range(0,len(policy_tree)):
                        element=convert(df_sub.loc[0,"Regulation"],policy_tree[j],p_color)
                        temp_sub['children'].append(element)
                chart_data=json.dumps(final_tree,indent=2)
                group_chart_data_list.append(chart_data)
            groups.reverse()
            group_chart_data_list.reverse()
            # print(group_chart_data_list)
            #graph for individual of business activities
        single_df=ProcessReg.objects.filter(user=request.user,category='Individual').values_list('businessdefinition_a','regulation','process')
        if single_df:
            df2=pd.DataFrame(list(single_df),columns=['Business_Definition','Regulation','Policy'])
            # df2=df.Policy.apply(pd.Series).merge(df, right_index = True, left_index = True).drop(["Policy"], axis = 1).melt(id_vars = ['Business_Definition','Regulation'], value_name = "Policy").drop("variable", axis = 1).dropna()
            n=len(individuals)#to store number of business activities for current user
            #parent,child mapping
            for l in range(0,n):
                df3=df2[df2['Business_Definition']==individuals[l]]
                df3.reset_index(inplace = True, drop = True) 
                b_color="#4d88ff"
                final_tree=convert("Null",df3.loc[0,"Business_Definition"],b_color)

                Reg_Tree=df3["Regulation"].unique().tolist()
                re_color="burlywood"
                for i in range(0,len(Reg_Tree)):
                    element=convert(df3.loc[0,"Business_Definition"],Reg_Tree[i],re_color)
                    final_tree['children'].append(element) 
                temp=final_tree['children'].copy()
                p_color="#99ff99"
                for i in range(0,len(temp)):
                    temp_sub=temp[i].copy()
                    df_sub=df3[df3['Regulation']==temp_sub['name']]
                    df_sub.reset_index(drop=True,inplace=True)
                    policy_tree=df_sub["Policy"].unique().tolist()
                    for j in range(0,len(policy_tree)):
                        element=convert(df_sub.loc[0,"Regulation"],policy_tree[j],p_color)
                        temp_sub['children'].append(element)
                chart_data=json.dumps(final_tree,indent=2)
                single_chart_data_list.append(chart_data)
            individuals.reverse()
            single_chart_data_list.reverse()
        context = {'table': table, 'flag' : button_enable,'group_data':group_chart_data_list,'single_data':single_chart_data_list,'individuals':individuals, 'groups':groups, 'user' : current_user}
        return render(request,'control_1.html/',context)

""" Method to Display the Control Reg Table
Input : Control Reg Table (Model)
Output : Risk Table """
@login_required
def selectrisk(request):
        # balist=request.session['balist']
        current_user=request.user
        count =ControlReg.objects.filter(user=current_user).count()  # Enable, Disable the Next Button
        done_count=ControlReg.objects.filter(user=current_user, status='done').count()
        if count == done_count:
           button_enable = True
        else:
           button_enable = False
        table = RiskTable(ControlReg.objects.filter(user=current_user))  # Configuring the Risk Table with Control Reg Table Data
        RequestConfig(request).configure(table)
        group=request.session['group']
         #graph for group of business activities
        groups=[]
        individuals=[]
        grouplist=ControlReg.objects.filter(user=request.user).exclude(category='Individual').values_list('category')
        individualist=ControlReg.objects.filter(user=request.user,category='Individual').values_list('businessdefinition_a')
        grouplist=list(grouplist)
        individualist=list(individualist)
        for group in grouplist:
            if group not in groups:
                groups.append(group[0])
        for single in individualist:
            individuals.append(single[0])
        groups=list(set(groups))
        individuals=list(set(individuals))
        single_chart_data_list=[]#to store json data for each business activity
        group_chart_data_list=[]#to store json data for each business activity
        # name=request.session['groupname']
        group_df=ControlReg.objects.filter(user=request.user).exclude(category='Individual').values_list('category','regulation','process','controlarea')
        if group_df:
            df2=pd.DataFrame(list(group_df),columns=['Business_Definition','Regulation','Policy','Control'])   
            # df2=df.Control.apply(pd.Series).merge(df, right_index = True, left_index = True).drop(["Control"], axis = 1).melt(id_vars = ['Business_Definition','Regulation','Policy'], value_name = "Control").drop("variable", axis = 1).dropna()
            for l in range(0,len(groups)):
                df3=df2[df2['Business_Definition']==groups[l]]
                
                df3.reset_index(inplace = True, drop = True)
                # print("***************************************")
                # print(df3)
                b_color="#4d88ff"
                final_tree=convert("Null",df3.loc[0,"Business_Definition"],b_color)
                # print(final_tree)
                Reg_Tree=df3["Regulation"].unique().tolist()
                re_color="burlywood"
                for i in range(0,len(Reg_Tree)):
                    element=convert(df3.loc[0,"Business_Definition"],Reg_Tree[i],re_color)
                    final_tree['children'].append(element)
                temp=final_tree['children'].copy()
                p_color="99ff99"
                for i in range(0,len(temp)):
                    temp_sub=temp[i].copy()
                    df_sub=df3[df3['Regulation']==temp_sub['name']]
                    df_sub.reset_index(drop=True,inplace=True)
                    policy_tree=df_sub["Policy"].unique().tolist()
                    for j in range(0,len(policy_tree)):
                        element=convert(df_sub.loc[0,"Regulation"],policy_tree[j],p_color)
                        temp_sub['children'].append(element)           
                p1=final_tree["children"]
                c_color="lightsalmon"
                for i in range(0,len(p1)):
                    p2=final_tree["children"][i]["children"]
                    for k in range(0,len(p2)):
                        p3=final_tree["children"][i]["children"][k]
                        df_sub2=df3[df3['Policy']==p3["name"]]        
                        df_sub2=df_sub2[df_sub2["Regulation"]==p3["parent"]]
                        df_sub2.reset_index(drop=True,inplace=True)   
                        control_tree=df_sub2["Control"].unique().tolist()   
                        for j in range(0,len(control_tree)):
                            element=convert(df_sub2.loc[0,"Policy"],control_tree[j],c_color)
                            p3['children'].append(element)   
                chart_data=json.dumps(final_tree,indent=2)
                group_chart_data_list.append(chart_data)
            controls = Controls.objects.filter(user=current_user).all()
            groups.reverse()
            group_chart_data_list.reverse()
        #graph for individual of business activities
        single_df=ControlReg.objects.filter(user=request.user,category='Individual').values_list('businessdefinition_a','regulation','process','controlarea')
        if single_df:
            df=pd.DataFrame(list(single_df),columns=['Business_Definition','Regulation','Policy','Control'])
            df2=df.Control.apply(pd.Series).merge(df, right_index = True, left_index = True).drop(["Control"], axis = 1).melt(id_vars = ['Business_Definition','Regulation','Policy'], value_name = "Control").drop("variable", axis = 1).dropna()
            n=len(individuals)#to store number of business activities for current user
            #parent,child mapping
            for l in range(0,n):
                        df3=df2[df2['Business_Definition']==individuals[l]]
                        df3.reset_index(inplace = True, drop = True) 
                        b_color="#4d88ff"
                        final_tree=convert("Null",df3.loc[0,"Business_Definition"],b_color)
                        Reg_Tree=df3["Regulation"].unique().tolist()
                        re_color="burlywood"
                        for i in range(0,len(Reg_Tree)):
                            element=convert(df3.loc[0,"Business_Definition"],Reg_Tree[i],re_color)
                            final_tree['children'].append(element) 
                        temp=final_tree['children'].copy()
                        p_color="99ff99"
                        for i in range(0,len(temp)):
                            temp_sub=temp[i].copy()
                            df_sub=df3[df3['Regulation']==temp_sub['name']]
                            df_sub.reset_index(drop=True,inplace=True)
                            policy_tree=df_sub["Policy"].unique().tolist()
                            for j in range(0,len(policy_tree)):
                                element=convert(df_sub.loc[0,"Regulation"],policy_tree[j],p_color)
                                temp_sub['children'].append(element)         
                        p1=final_tree["children"]
                        c_color="lightsalmon"
                        for i in range(0,len(p1)):
                            p2=final_tree["children"][i]["children"]
                            for k in range(0,len(p2)):
                                p3=final_tree["children"][i]["children"][k]
                                df_sub2=df3[df3['Policy']==p3["name"]]        
                                df_sub2=df_sub2[df_sub2["Regulation"]==p3["parent"]]
                                df_sub2.reset_index(drop=True,inplace=True)   
                                
                                control_tree=df_sub2["Control"].unique().tolist()   
                                for j in range(0,len(control_tree)):
                                    element=convert(df_sub2.loc[0,"Policy"],control_tree[j],c_color)
                                    p3['children'].append(element)   

                        chart_data=json.dumps(final_tree,indent=2)
                        single_chart_data_list.append(chart_data)
            individuals.reverse()
            single_chart_data_list.reverse()
        controls = Controls.objects.filter(user=current_user).all()
        context = {'table': table, 'flag' : button_enable,'group_data':group_chart_data_list,'single_data':single_chart_data_list,'individuals':individuals, 'groups':groups, 'user' : current_user, 'controls': controls}
        return render(request,'Risk_1.html/',context)


"""  Method for selection of Risk
Input : Risk Form Set
Output: Saving corresponding mapping in RiskReg Table (Model) """
@login_required  
def select_risk(request, pk):
    item = get_object_or_404(ControlReg, id=pk)
    heading_message = 'Risk Management'
    user=request.user
    if request.method == 'POST':
        formset = RiskFormSet(request.POST)   # Displaying the Risk Form Set
        if formset.is_valid():
            ControlReg.objects.filter(pk=pk).update(status='done')
            for form in formset:
                # Extracting the data from Risk Form Set
                risk= form.cleaned_data.get('risk')
                comment = form.cleaned_data.get('comment')
                description = form.cleaned_data.get('description')
                RiskReg(regulation=item.regulation, businessdefinition_a = item.businessdefinition_a, businessdefinition_q = item.businessdefinition_q, jurisdiction=item.jurisdiction, 
                process=item.process, description=item.description, controlarea=item.controlarea, controldescription=item.controldescription, 
                controlobjective=item.controlobjective, risk=risk, comment=comment, riskdescription=description, user=user,category=item.category).save()  # Saving the Selected data into Risk Reg Table (Model)
            return redirect('selectrisk')
    else:
        formset = RiskFormSet(request.GET or None)

    return render(request, 'Risk_2.html', {
        'formset': formset,
        'heading': heading_message,
        'user' : user
    })


""" Method to display Risk Reg Table
Input : Risk Reg Table (Model)
Output : Final Table """
@login_required
def showfinalmapping(request):
    # temp=request.session['risk']
    current_user=request.user
    count =RiskReg.objects.filter(user=current_user).count()  # Enable, Disable Next Button
    done_count=RiskReg.objects.filter(user=current_user, status='done').count()
    if count == done_count:
       button_enable = True
    else:
       button_enable = False
    table = FinalTable(RiskReg.objects.filter(user=current_user)) # Configuring the Risk Reg Data in Final Table
    RequestConfig(request).configure(table)
    groups=[]
    individuals=[]
    grouplist=RiskReg.objects.filter(user=request.user).exclude(category='Individual').values_list('category')
    individualist=RiskReg.objects.filter(user=request.user,category='Individual').values_list('businessdefinition_a')
    grouplist=list(grouplist)
    individualist=list(individualist)
    for group in grouplist:
        if group not in groups:
            groups.append(group[0])
    for single in individualist:
        individuals.append(single[0])
    groups=list(set(groups))
    individuals=list(set(individuals))
    group_chart_data_list=[]#to store json data for each business activity
    single_chart_data_list=[]#to store json data for each business activity
    ## Grpah for group
    # name=request.session['groupname']
    group_df=RiskReg.objects.filter(user=request.user).exclude(category='Individual').values_list('category','regulation','process','controlarea','risk')
    if group_df:
        df1=pd.DataFrame(list(group_df),columns=['Business_Definition','Regulation','Policy','Control','Risk'])
        # print(df1)
        # print(groups)
        # df2=df.Risk.apply(pd.Series).merge(df, right_index = True, left_index = True).drop(["Risk"], axis = 1).melt(id_vars = ['Business_Definition','Regulation','Policy','Control'], value_name = "Risk").drop("variable", axis = 1).dropna()
        for l in range(0,len(groups)):
            df2=df1[df1['Business_Definition']==groups[l]]
            # print(df3)
            df2.reset_index(inplace = True, drop = True)
            # print("############################################################")
            # print(df2)
            b_color="#4d88ff"
            final_tree=convert("Null",df2.loc[0,"Business_Definition"],b_color)
            Reg_Tree=df2["Regulation"].unique().tolist()
            re_color="burlywood"
            for i in range(0,len(Reg_Tree)):
                element=convert(df2.loc[0,"Business_Definition"],Reg_Tree[i],re_color)
                final_tree['children'].append(element)
            temp=final_tree['children'].copy()
            p_color="99ff99"
            for i in range(0,len(temp)):
                temp_sub=temp[i].copy()
                df_sub=df2[df2['Regulation']==temp_sub['name']]
                df_sub.reset_index(drop=True,inplace=True)
                policy_tree=df_sub["Policy"].unique().tolist()
                for j in range(0,len(policy_tree)):
                    element=convert(df_sub.loc[0,"Regulation"],policy_tree[j],p_color)
                    temp_sub['children'].append(element)         
            p1=final_tree["children"]
            c_color="lightsalmon"
            for i in range(0,len(p1)):
                p2=final_tree["children"][i]["children"]
                for k in range(0,len(p2)):
                    p3=final_tree["children"][i]["children"][k]
                    df_sub2=df2[df2['Policy']==p3["name"]]        
                    df_sub2=df_sub2[df_sub2["Regulation"]==p3["parent"]]
                    df_sub2.reset_index(drop=True,inplace=True)     
                    control_tree=df_sub2["Control"].unique().tolist()   
                    for j in range(0,len(control_tree)):
                        element=convert(df_sub2.loc[0,"Policy"],control_tree[j],c_color)
                        p3['children'].append(element)                 
            m1=final_tree["children"]
            risk_color="powerblue" 
            for i in range(0,len(m1)):
                m2=final_tree["children"][i]["children"]       
                for k in range(0,len(m2)):
                    m3=final_tree["children"][i]["children"][k]["children"]
                    for q in range(0,len(m3)):
                        m4= final_tree["children"][i]["children"][k]["children"][q]
                        df_sub3=df2[df2['Control']==m4["name"]]  
                        df_sub3.reset_index(drop=True,inplace=True)
                        df_sub3= df_sub3[ df_sub3['Policy']==m4["parent"]]        
                        df_sub3=df_sub3[df_sub3["Regulation"]==m2[0]["parent"]]
                        df_sub3.reset_index(drop=True,inplace=True)     
                        risk_tree=df_sub3["Risk"].unique().tolist()   
                        for j in range(0,len(risk_tree)):
                            element=convert(df_sub3.loc[0,"Control"],risk_tree[j],risk_color)
                            m4['children'].append(element)                        
            chart_data=json.dumps(final_tree,indent=2)
            group_chart_data_list.append(chart_data)
        groups.reverse()
        group_chart_data_list.reverse()
    #graph for individual of business activities
    single_df=RiskReg.objects.filter(user=request.user,category='Individual').values_list('businessdefinition_a','regulation','process','controlarea','risk')
    if single_df:
        df2=pd.DataFrame(list(single_df),columns=['Business_Definition','Regulation','Policy','Control','Risk'])
        # df2=df.Risk.apply(pd.Series).merge(df, right_index = True, left_index = True).drop(["Risk"], axis = 1).melt(id_vars = ['Business_Definition','Regulation','Policy','Control'], value_name = "Risk").drop("variable", axis = 1).dropna()
        
        n=len(individuals)#to store number of business activities for current user
        #parent,child mapping
        for l in range(0,n):
                    df3=df2[df2['Business_Definition']==individuals[l]]
                    df3.reset_index(inplace = True, drop = True) 
                    b_color="#4d88ff"
                    final_tree=convert("Null",df3.loc[0,"Business_Definition"],b_color)
                    Reg_Tree=df3["Regulation"].unique().tolist()
                    r_color="burlywood"
                    for i in range(0,len(Reg_Tree)):
                        element=convert(df3.loc[0,"Business_Definition"],Reg_Tree[i],r_color)
                        final_tree['children'].append(element)                       
                    temp=final_tree['children'].copy()
                    p_color="#99ff99"
                    for i in range(0,len(temp)):
                        temp_sub=temp[i].copy()
                        df_sub=df3[df3['Regulation']==temp_sub['name']]
                        df_sub.reset_index(drop=True,inplace=True)
                        policy_tree=df_sub["Policy"].unique().tolist()
                        for j in range(0,len(policy_tree)):
                            element=convert(df_sub.loc[0,"Regulation"],policy_tree[j],p_color)
                            temp_sub['children'].append(element)           
                    p1=final_tree["children"]
                    c_color="lightsalmon"
                    for i in range(0,len(p1)):
                        p2=final_tree["children"][i]["children"]
                        for k in range(0,len(p2)):
                            p3=final_tree["children"][i]["children"][k]
                            df_sub2=df3[df3['Policy']==p3["name"]]        
                            df_sub2=df_sub2[df_sub2["Regulation"]==p3["parent"]]
                            df_sub2.reset_index(drop=True,inplace=True)     
                            control_tree=df_sub2["Control"].unique().tolist()   
                            for j in range(0,len(control_tree)):
                                element=convert(df_sub2.loc[0,"Policy"],control_tree[j],c_color)
                                p3['children'].append(element)                
                    m1=final_tree["children"]
                    risk_color="powerblue" 
                    for i in range(0,len(m1)):
                        m2=final_tree["children"][i]["children"]       
                        for k in range(0,len(m2)):
                            m3=final_tree["children"][i]["children"][k]["children"]
                            for q in range(0,len(m3)):
                                m4= final_tree["children"][i]["children"][k]["children"][q]
                                df_sub3=df3[df3['Control']==m4["name"]]  
                                df_sub3.reset_index(drop=True,inplace=True)
                                df_sub3= df_sub3[ df_sub3['Policy']==m4["parent"]]        
                                df_sub3=df_sub3[df_sub3["Regulation"]==m2[0]["parent"]]
                                df_sub3.reset_index(drop=True,inplace=True)     
                                risk_tree=df_sub3["Risk"].unique().tolist()   
                                for j in range(0,len(risk_tree)):
                                    element=convert(df_sub3.loc[0,"Control"],risk_tree[j],risk_color)
                                    m4['children'].append(element)                  
                    chart_data=json.dumps(final_tree,indent=2)
                    single_chart_data_list.append(chart_data)
        individuals.reverse()
        single_chart_data_list.reverse()
    # context = {'table': table, 'flag' : button_enable,'group_data':group_chart_data_list,'sing' 'user' : current_user}
    context = {'table': table, 'flag' : button_enable,'group_data':group_chart_data_list,'single_data':single_chart_data_list,'individuals':individuals, 'groups':groups, 'user' : current_user}
    return render(request,'Risk_3.html/',context)


""" Method for Edit Regulation
Input : Edit Regulation Form, With single select(Radio Button)
Output: Selected Regulation (Which is to be updated), will be saved in BAReg Table (Model) """
@login_required
def edit_regulation(request, pk):
    heading_message='Edit Regulation Management'
    user=request.user
    if request.method == 'POST':
       form = EditRegulationForm(request.POST or None,prefix="form1")  # Edit Regulation Form
       if form.is_valid():
           regulation = form.cleaned_data.get('Regulation') # Extracting the regulation, which is to be updated
           BAReg.objects.filter(id=pk).update(regulation=regulation, edit_status='done') # Updating the regulation
           return redirect('secondpage')
    else:
           form = EditRegulationForm(request.GET or None, prefix="form1") 
    return render(request,'Edit_Regulation.html/', { 'form' : form,
           'heading' : heading_message,
           'user' : user
           })   


""" Method for Edit Process
Input : Process Form Set
Output : Process Which is to be updated, will be saved in ProcessReg Table (Model) """
@login_required
def edit_process(request, pk):
    heading_message = 'Edit Process Management'
    user=request.user
    if request.method == 'POST':
        formset = ProcessFormSet(request.POST)  # Displaying the Process Form for Edit
        if formset.is_valid():
            for form in formset:        # Extracting the data from Process Form 
                title=form.cleaned_data.get('title')
                description=form.cleaned_data.get('description')
                ProcessReg.objects.filter(id=pk).update(process=title, description=description, edit_status='done')  # Updating the Process in Process Reg Table
                request.session['title']=title
                return redirect('selectcontrol')
    else:
            formset = ProcessFormSet(request.GET or None)
    return render(request,'Edit_Process.html/', {'formset':formset,
    'heading': heading_message,
    'user' : user
    })


""" Method for Edit Control
Input : Control Form Set
Output : Control Which is to be updated, will be saved in ControlReg Table (Model) """
@login_required
def edit_control(request,pk):
    heading_message = 'Edit Control Management'
    if request.method == 'POST':
        formset = ControlFormSet(request.POST)   # Displaying the Control Form for Edit     
        if formset.is_valid():
            for form in formset:  # Extracting the Controls from the form
                control=form.cleaned_data.get('control') 
                description=form.cleaned_data.get('description')
                content=form.cleaned_data.get('content')
                request.session['control']=control
                ControlReg.objects.filter(id=pk).update(controlarea=control, controlobjective=description,controldescription=content, edit_status='done')
                # Updating the selected controls in Control Reg Table
                return redirect('selectrisk')
    else:
            formset = ControlFormSet(request.GET or None)
            return render(request,'Edit_Control.html/', {'formset':formset,
            'heading' : heading_message
            })


""" Method for Edit Risk
Input : Risk Form Set
Output : Risk Which is to be updated will be saved in RiskReg Table (Model) """
@login_required
def edit_risk(request,pk):
    heading_message='Edit Risk Management'
    user=request.user
    if request.method == 'POST':
        formset = RiskFormSet(request.POST)     # Displaying the Risk Form for Edit   
        if formset.is_valid():
           for form in formset:  # Extracting the data from Risk Form
               risk=form.cleaned_data.get('risk')
               comment=form.cleaned_data.get('comment')
               request.session['risk']=risk
               RiskReg.objects.filter(id=pk).update(risk=risk, comment=comment, edit_status='done') # Updating the Risk in Risk Reg Table (Model)
               return redirect('showfinalmapping')
    else:
            formset = RiskFormSet(request.GET or None)
            return render(request,'Edit_Risk.html/', {'formset':formset,
            'heading' : heading_message,
            'user' : user
            })

""" Method for displaying the Risk Reg in Finalview Table
Input : Risk Reg Table (Model)
Output : Final view Table """
@login_required
def viewfinalmapping(request):
    groups=[]
    individuals=[]
    grouplist=RiskReg.objects.filter(user=request.user).exclude(category='Individual').values_list('category')
    individualist=RiskReg.objects.filter(user=request.user,category='Individual').values_list('businessdefinition_a')
    grouplist=list(grouplist)
    individualist=list(individualist)
    for group in grouplist:
        if group not in groups:
            groups.append(group[0])
    for single in individualist:
        individuals.append(single[0])
    groups=list(set(groups))
    individuals=list(set(individuals))
    ba = request.session.get('ba')
    current_user=request.user
    balist=request.session['balist']
    group=request.session['group']
    name=request.session['groupname']
  
    if group == 'yes':   # Ig group is yes, Remove temp group name in all tables, as many balist times, for a specific user
        set1=RiskReg.objects.filter(user=request.user,businessdefinition_a='Group - '+name)
        BAReg.objects.filter(user=request.user, businessdefinition_a='Group - '+name).delete()
        ControlReg.objects.filter(user=request.user, businessdefinition_a='Group - '+name).delete()
        ProcessReg.objects.filter(user=request.user, businessdefinition_a='Group - '+name).delete()
        for x in set1:
            for ba in balist:
                count1=RiskReg.objects.filter(regulation=x.regulation,businessdefinition_a=ba,process=x.process,controlarea=x.controlarea,risk=x.risk, user=request.user,category=name).count()
                if(count1<1):   # To avoid duplicates
                    RiskReg(regulation=x.regulation,businessdefinition_a=ba,process=x.process,controlarea=x.controlarea,risk=x.risk, user=request.user,status='done',category=name).save()
                    ControlReg(regulation=x.regulation,businessdefinition_a=ba,process=x.process,controlarea=x.controlarea, user=request.user,status='done',category=name).save()
                    ProcessReg(regulation=x.regulation,businessdefinition_a=ba,process=x.process, user=request.user,status='done',category=name).save()
                    BAReg(regulation=x.regulation,businessdefinition_a=ba,user=request.user,status='done',category=name).save()
        RiskReg.objects.filter(user=request.user,businessdefinition_a='Group - '+name).delete()
    table = FinalviewTable(RiskReg.objects.filter(user=current_user))  # Configuring the Final view Table with Risk Reg Data
    RequestConfig(request).configure(table)
    # items=RiskReg.objects.filter(user=current_user)#retrieve all current user data from RiskReg table
    # balist=['Group']#default name to group



    single_chart_data_list=[]#to store json data for each business activity
    group_chart_data_list=[]#to store json data for each business activity

    #graph for group of business activities
    name=request.session['groupname']
    group_df=RiskReg.objects.filter(user=request.user).exclude(category='Individual').values_list('category','regulation','process','controlarea','risk')
    df2=pd.DataFrame(list(group_df),columns=['Business_Definition','Regulation','Policy','Control','Risk'])
    n=len(groups)#to store number of business activities for current user
    for l in range(0,n):
        df3=df2[df2['Business_Definition']==groups[l]]
        df3.reset_index(inplace = True, drop = True) 
        b_color="#4d88ff"
        final_tree=convert("Null",df3.loc[0,"Business_Definition"],b_color)
        Reg_Tree=df3["Regulation"].unique().tolist()
        r_color="burlywood"
        for i in range(0,len(Reg_Tree)):
            element=convert(df3.loc[0,"Business_Definition"],Reg_Tree[i],r_color)
            final_tree['children'].append(element)
        temp=final_tree['children'].copy()
        p_color="#99ff99"
        for i in range(0,len(temp)):
            temp_sub=temp[i].copy()
            df_sub=df3[df3['Regulation']==temp_sub['name']]
            df_sub.reset_index(drop=True,inplace=True)
            policy_tree=df_sub["Policy"].unique().tolist()
            for j in range(0,len(policy_tree)):
                element=convert(df_sub.loc[0,"Regulation"],policy_tree[j],p_color)
                temp_sub['children'].append(element)          
        p1=final_tree["children"]
        c_color="lightsalmon"
        for i in range(0,len(p1)):
            p2=final_tree["children"][i]["children"]
            for k in range(0,len(p2)):
                p3=final_tree["children"][i]["children"][k]
                df_sub2=df3[df3['Policy']==p3["name"]]        
                df_sub2=df_sub2[df_sub2["Regulation"]==p3["parent"]]
                df_sub2.reset_index(drop=True,inplace=True)     
                control_tree=df_sub2["Control"].unique().tolist()   
                for j in range(0,len(control_tree)):
                    element=convert(df_sub2.loc[0,"Policy"],control_tree[j],c_color)
                    p3['children'].append(element)               
        m1=final_tree["children"]
        risk_color="powerblue" 
        for i in range(0,len(m1)):
            m2=final_tree["children"][i]["children"]       
            for k in range(0,len(m2)):
                m3=final_tree["children"][i]["children"][k]["children"]
                for q in range(0,len(m3)):
                    m4= final_tree["children"][i]["children"][k]["children"][q]
                    df_sub3=df3[df3['Control']==m4["name"]]  
                    df_sub3.reset_index(drop=True,inplace=True)
                    df_sub3= df_sub3[ df_sub3['Policy']==m4["parent"]]        
                    df_sub3=df_sub3[df_sub3["Regulation"]==m2[0]["parent"]]
                    df_sub3.reset_index(drop=True,inplace=True)     
                    risk_tree=df_sub3["Risk"].unique().tolist()   
                    for j in range(0,len(risk_tree)):
                        element=convert(df_sub3.loc[0,"Control"],risk_tree[j],risk_color)
                        m4['children'].append(element)                     
        chart_data=json.dumps(final_tree,indent=2)
        group_chart_data_list.append(chart_data)
    groups.reverse()
    group_chart_data_list.reverse()    


    #graph for individual of business activities
    single_df=RiskReg.objects.filter(user=request.user,category='Individual').values_list('businessdefinition_a','regulation','process','controlarea','risk')
    df2=pd.DataFrame(list(single_df),columns=['Business_Definition','Regulation','Policy','Control','Risk'])
    n=len(individuals)#to store number of business activities for current user
    #parent,child mapping
    for l in range(0,n):
        df3=df2[df2['Business_Definition']==individuals[l]]
        df3.reset_index(inplace = True, drop = True)
        b_color="#4d88ff"
        final_tree=convert("Null",df3.loc[0,"Business_Definition"],b_color)
        Reg_Tree=df3["Regulation"].unique().tolist()
        r_color="burlywood"
        for i in range(0,len(Reg_Tree)):
            element=convert(df3.loc[0,"Business_Definition"],Reg_Tree[i],r_color)
            final_tree['children'].append(element)
        temp=final_tree['children'].copy()
        p_color="#99ff99"
        for i in range(0,len(temp)):
            temp_sub=temp[i].copy()
            df_sub=df3[df3['Regulation']==temp_sub['name']]
            df_sub.reset_index(drop=True,inplace=True)
            policy_tree=df_sub["Policy"].unique().tolist()
            for j in range(0,len(policy_tree)):
                element=convert(df_sub.loc[0,"Regulation"],policy_tree[j],p_color)
                temp_sub['children'].append(element)          
        p1=final_tree["children"]
        c_color="lightsalmon"
        for i in range(0,len(p1)):
            p2=final_tree["children"][i]["children"]
            for k in range(0,len(p2)):
                p3=final_tree["children"][i]["children"][k]
                df_sub2=df3[df3['Policy']==p3["name"]]        
                df_sub2=df_sub2[df_sub2["Regulation"]==p3["parent"]]
                df_sub2.reset_index(drop=True,inplace=True)     
                control_tree=df_sub2["Control"].unique().tolist()   
                for j in range(0,len(control_tree)):
                    element=convert(df_sub2.loc[0,"Policy"],control_tree[j],c_color)
                    p3['children'].append(element)                   
        m1=final_tree["children"]
        risk_color="powerblue" 
        for i in range(0,len(m1)):
            m2=final_tree["children"][i]["children"]       
            for k in range(0,len(m2)):
                m3=final_tree["children"][i]["children"][k]["children"]
                for q in range(0,len(m3)):
                    m4= final_tree["children"][i]["children"][k]["children"][q]
                    df_sub3=df3[df3['Control']==m4["name"]]  
                    df_sub3.reset_index(drop=True,inplace=True)
                    df_sub3= df_sub3[ df_sub3['Policy']==m4["parent"]]        
                    df_sub3=df_sub3[df_sub3["Regulation"]==m2[0]["parent"]]
                    df_sub3.reset_index(drop=True,inplace=True)     
                    risk_tree=df_sub3["Risk"].unique().tolist()   
                    for j in range(0,len(risk_tree)):
                        element=convert(df_sub3.loc[0,"Control"],risk_tree[j],risk_color)
                        m4['children'].append(element)                    
        chart_data=json.dumps(final_tree,indent=2)
        single_chart_data_list.append(chart_data)   
    individuals.reverse()
    single_chart_data_list.reverse()   
           

    table = FinalviewTable(RiskReg.objects.filter(user=current_user))

    context = {'table': table,'group_data':group_chart_data_list, 'single_data': single_chart_data_list,'individuals':individuals, 'groups':groups,'user' : current_user}
    return render(request,'finalview.html/',context)


""" Method to delete a specific Mapping 
Input : Based on Specific id, Deletion happens in all Tables.
Output: Selected ID specific mapping will be deleted in all the tables """
@login_required
def deleteMapping(request,pk):
    items=RiskReg.objects.filter(id=pk).all()  # Key id for deletion
    for item in items:
        Business.objects.filter(businessactivity=item.businessdefinition_a, user=request.user).delete()
        BAReg.objects.filter(regulation=item.regulation, businessdefinition_a=item.businessdefinition_a, user=request.user).delete()
        ProcessReg.objects.filter(regulation=item.regulation, businessdefinition_a=item.businessdefinition_a, process=item.process, description=item.description, user=request.user).delete()
        ControlReg.objects.filter(regulation=item.regulation, businessdefinition_a=item.businessdefinition_a, process=item.process, description=item.description, controlarea=item.controlarea,
        controlobjective=item.controlobjective, controldescription=item.controldescription, user=request.user).delete()
    RiskReg.objects.filter(id=pk).delete()
    return redirect('showfinalmapping')

""" Method to reset Mapping 
Input: The Specific User
Output: Mapping will delete from all the table, and starts from Begin """
@login_required
def resetMapping(request):
    balist  = request.session.get('balist') 
    group=request.session['group'] 
    name=request.session['groupname']
    if group == 'yes': 
        for ba in balist:
           BusinessGroup.objects.filter(groupname=name).delete()
           BAReg.objects.filter(businessdefinition_a = 'Group - '+name).delete()
           ProcessReg.objects.filter(businessdefinition_a = 'Group - '+name).delete()
           ControlReg.objects.filter(businessdefinition_a = 'Group - '+name).delete()
           RiskReg.objects.filter(businessdefinition_a = 'Group - '+name).delete()
        return redirect('selectbusiness')
    else:
        Business.objects.filter(businessactivity__in = balist).delete() 
        for ba in balist:
            BAReg.objects.filter(businessdefinition_a = ba).delete()
            ProcessReg.objects.filter(businessdefinition_a = ba).delete()
            ControlReg.objects.filter(businessdefinition_a = ba).delete()
            RiskReg.objects.filter(businessdefinition_a = ba).delete()
        return redirect('selectbusiness')

@login_required
def firstpage(request):
        current_user=request.user
       
        count =Business.objects.filter(user=current_user).count()
        done_count=Business.objects.filter(user=current_user, status='done').count()
        if count == done_count:
           button_enable = True
        else:
           button_enable = False
        table = BusinessTable(Business.objects.filter(user=current_user))
        RequestConfig(request).configure(table)
        context = {'table': table, 'flag' : button_enable, 'user': current_user}
        return render(request,'Reg1.html/',context)


""" Method for Edit Business Activity
Input : Edit Business Form, Which allows user to select single option (Radio Button)
Output: Selected BA (BA, which is to be updated) will be saved in Business Table """
@login_required
def edit_businessactivity(request, pk):
   heading_message='Edit Business Management'
   user=request.user
   if request.method == 'POST':
      form = EditBusinessForm(request.POST or None,prefix="form1") # Displaying the Edit Business Form
      if form.is_valid():  # Extracting the data from Edit Business Form
          businessactivitites=form.cleaned_data.get('Business_Activities')
          jurisdiction = form.cleaned_data.get('Jurisdiction')
          updated_ba=str(businessactivitites.businessdefinition_q)+str("/")+str(businessactivitites.businessdefinition_a)+str("/")+str(jurisdiction)
          group=request.POST.get('groupall')
          request.session['group']=group
          Business.objects.filter(id=pk).update(businessactivity=updated_ba, edit_status='done', user=user) #Updating the BA
          return redirect('firstpage')
   else:
          form = EditBusinessForm(prefix="form1")
   return render(request,'Edit_Business.html/', { 'form' : form,
          'heading' : heading_message, 
          'user' : user
          })


""" Method for Adding Regulation (Individual)
Input : Business Table BA's
Output : Slected Regulations (for corresponding BA's) will be saved in BAReg Mapping Table """
@login_required
def addregulation(request, pk):
    item = get_object_or_404(Business, id=pk) 
    items=Regulations.objects.all()
    user=request.user
    heading_message = 'Regulation Management'
    if request.method == 'POST':
        form = RegulationForm(request.POST)   # Displaying the Regultions
        if form.is_valid():  # Extracting the data from Regulation Form
            Business.objects.filter(pk=pk).update(status='done')
            regulations= form.cleaned_data.get('Regulations')
            for regulation in regulations:
                BAReg(regulation=regulation, businessdefinition_a = item.businessactivity, user=user).save() 
                # Slected Regulations (for corresponding BA's) will be saved in BAReg Mapping Table
            return redirect('firstpage')
       
    else:
        form = RegulationForm(request.GET or None)
    return render(request, 'Reg2.html', {
        'form': form,
        'heading': heading_message,
        'items':items,
        'user': user
    })

""" Method for Reset Business and BAReg Table (Model) """
@login_required
def reset_mapping_bareg(request):
   balist  = request.session.get('balist')   
   Business.objects.filter(businessactivity__in = balist).delete() 
   for ba in balist:
       BAReg.objects.filter(businessdefinition_a = ba).delete()
   return redirect('selectbusiness')


""" Method for Reset Business, BAReg and Process Table (Model) """
@login_required
def reset_mapping_bareg_group(request):
   balist  = request.session.get('balist')
   group=request.session['group'] 
   name=request.session['groupname']  
   if group == "yes":
        BAReg.objects.filter(businessdefinition_a = 'Group - '+name).delete() 
        for ba in balist:
            BusinessGroup.objects.filter(groupname=name).delete()
            ProcessReg.objects.filter(businessdefinition_a = 'Group - '+name).delete()
        return redirect('selectbusiness')
   else:
        Business.objects.filter(businessactivity__in = balist).delete()
        for ba in balist:
           BAReg.objects.filter(businessdefinition_a = ba).delete()
           ProcessReg.objects.filter(businessdefinition_a = ba).delete()
        return redirect('selectbusiness')

@login_required
def RMControl(request):
    balist  = request.session.get('balist') 
    group=request.session['group'] 
    name=request.session['groupname']
    if group == 'yes': 
        ControlReg.objects.filter(businessdefinition_a = 'Group - '+name).delete()
        for ba in balist:
           BusinessGroup.objects.filter(groupname=name).delete()
           BAReg.objects.filter(businessdefinition_a = 'Group - '+name).delete()
           ProcessReg.objects.filter(businessdefinition_a = 'Group - '+name).delete()
        return redirect('selectbusiness')
    else:
        Business.objects.filter(businessactivity__in = balist).delete() 
        for ba in balist:
            BAReg.objects.filter(businessdefinition_a = ba).delete()
            ProcessReg.objects.filter(businessdefinition_a = ba).delete()  
        return redirect('selectbusiness')

@login_required
def RMRisk(request):
    balist  = request.session.get('balist') 
    group=request.session['group'] 
    name=request.session['groupname']
    if group == 'yes': 
        RiskReg.objects.filter(businessdefinition_a = 'Group - '+name).delete()
        for ba in balist:
           BusinessGroup.objects.filter(groupname=name).delete()
           BAReg.objects.filter(businessdefinition_a = 'Group - '+name).delete()
           ProcessReg.objects.filter(businessdefinition_a = 'Group - '+name).delete()
           ControlReg.objects.filter(businessdefinition_a = 'Group - '+name).delete()
        return redirect('selectbusiness')
    else:
        Business.objects.filter(businessactivity__in = balist).delete() 
        for ba in balist:
            BAReg.objects.filter(businessdefinition_a = ba).delete()
            ProcessReg.objects.filter(businessdefinition_a = ba).delete()
            ControlReg.objects.filter(businessdefinition_a = ba).delete()  
        return redirect('selectbusiness')

def showallmappings(request):
    ba = request.session.get('ba')
    current_user=request.user
    balist=request.session['balist']
    group=request.session['group']
    result=[]#to store table information as list
    chart_data_list=[]#to store json data for each business activity

    items=RiskReg.objects.filter(user=current_user)#retrieve all current user data from RiskReg table
    balist1=[]
    balist=[]
    reg=[]
    process=[]
    control=[]
    risk=[]
    for item in items:
        item_list=[]
        item_list.append(item.businessdefinition_a)
        balist.append(item.businessdefinition_a)
        if item.businessdefinition_a not in balist1:#unique business activities
            balist1.append(item.businessdefinition_a)
        item_list.append(item.regulation)
        item_list.append(item.process)
        item_list.append(item.controlarea)
        item_list.append(item.risk)
        reg.append(item.regulation)
        process.append(item.process)
        control.append(item.controlarea)
        risk.append(item.risk)
        result.append(item_list)
 
    df=pd.DataFrame(result,columns=["Business Definition","Regulation","Process","Control Area","Risk"])
    input=df

    output= pd.DataFrame()

    output["source"]=""
    output["target"]=""
    output["value"]=""
    # output["color"]=""

    iter1=input[["Business Definition","Regulation"]]
    iter1= iter1.drop_duplicates().reset_index(drop=True)
    iter1["value"]=1
    # iter1["color"]="red"
    iter1.columns=output.columns.values

    output=output.append(iter1)

    iter1=input[["Regulation","Process"]]
    iter1= iter1.drop_duplicates().reset_index(drop=True)
    iter1["value"]=1
    # iter1["color"]="blue"
    iter1.columns=output.columns.values

    output=output.append(iter1)

    iter1=input[["Process","Control Area"]]
    iter1= iter1.drop_duplicates().reset_index(drop=True)
    iter1["value"]=1
    # iter1["color"]="green"
    iter1.columns=output.columns.values

    output=output.append(iter1)


    iter1=input[["Control Area","Risk"]]
    iter1= iter1.drop_duplicates().reset_index(drop=True)
    iter1["value"]=1
    # iter1["color"]="yellow"
    iter1.columns=output.columns.values

    output=output.append(iter1)
    output.reset_index(drop=True, inplace=True)
    chart_data = output.to_dict(orient='records')
    chart_data = json.dumps(chart_data, indent=2,sort_keys=True, default=str)
   

    context = {'data':chart_data,'balist':balist,'reglist':reg,'process':process,'control':control,'risk':risk}
    return render(request,'Network.html/',context)



@login_required
def existingMapping(request):
   table = FinalviewTable(RiskReg.objects.filter(user=request.user))  # Configuring the RiskReg Table data in Final View Table
   RequestConfig(request).configure(table)
   context ={'table':table,'user':request.user}
   return render(request, 'final.html', context)

@login_required
def viewGroups(request):
    table = GroupTable(BusinessGroup.objects.filter(user=request.user))
    RequestConfig(request).configure(table)
    return render(request, 'groupdetails.html', { 'table' : table})