from django.urls import path

from . import views 



urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('homepage/', views.homepage, name='homepage'),
    path('home/', views.selectbusiness,  name='selectbusiness'),
    path('selectreg/', views.countries_view, name='countries_view'),
    path('bagroup/selectreg/', views.bagroupall, name="bagroupall"),
    path('table/',views.secondpage, name ="secondpage"),
    path('bagroup/table/', views.firstpage, name='firstpage'),
    path('bagroup/table/reset_bareg/', views.reset_mapping_bareg, name='reset_mapping_bareg'),
    path('bagroup/table/reset_bareg_group/', views.reset_mapping_bareg_group, name='reset_mapping_bareg_group'),
    path('table/edit/<int:pk>/', views.edit_item, name="edit_item"),
    path('table/selectcontrol/', views.selectcontrol, name='selectcontrol'),
    path('add_control/<int:pk>/', views.select_control, name="select_control"),
    path('table/selectcontrol/edit/process/<int:pk>/', views.edit_process,name="edit_process"),  #if we click on edit option in control page
    path('edit_control/<int:pk>/', views.select_control, name="select_control"), #if we click on add option in control page
    path('table/view_control',views.thirdpage, name ="thirdpage"),
    path('add_risk/<int:pk>/', views.select_risk, name="select_risk"),
    path('table/edit/regulation/<int:pk>/', views.edit_regulation,name="edit_regulation"),
    path('bagroup/table/edit/businessactivity/<int:pk>/', views.edit_businessactivity,name="edit_businessactivity"),
    path('bagroup/table/edit/<int:pk>/', views.addregulation, name="addregulation"),
    path('table/selectrisk/',views.selectrisk, name ="selectrisk"),
    path('edit_risk/<int:pk>/', views.select_risk, name="select_risk"),#if we click on add option in Risk page
    path('table/selectrisk/edit/control/<int:pk>/', views.edit_control,name="edit_control"),#if we click on edit option in risk page
    path('table/selectrisk/finalmapping/', views.showfinalmapping, name="showfinalmapping"),
    path('table/selectrisk/finalmapping/view/', views.viewfinalmapping, name="viewfinalmapping"),
    path('table/selectrisk/finalmapping/edit/risk/<int:pk>/', views.edit_risk, name="edit_risk"),#if we click on edit option in final mapping page
    path('table/selectrisk/finalmapping/delete_allmapping/<int:pk>/', views.deleteMapping, name="deleteMapping"),
    path('table/selectrisk/finalmapping/view/reset_mapping/', views.resetMapping, name='resetMapping'),
    path('table/selectrisk/edit/control/<int:pk>/', views.edit_control,name="edit_control"),
    path('risk/<int:pk>/', views.select_risk, name="select_risk"),
    path('resetmapping/', views.RMControl, name='RMControl'),
    path('risk_resetmapping/', views.RMRisk, name="RMRisk"),
    path('networkgraph/',views.showallmappings,name='showallmappings'),
    path('viewfinalmapping/', views.existingMapping, name='existingMapping'),
    path('viewusergroups/', views.viewGroups, name="viewGroups"),
    
   
]