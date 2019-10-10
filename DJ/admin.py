from django.contrib import admin

# Register your models here.
from .models import Regulations
from .models import *



admin.site.register(Regulations)
admin.site.register(BusinessActivity)
admin.site.register(BAReg)
# admin.site.register(Policy)
admin.site.register(ProcessReg)
# admin.site.register(Controls)
admin.site.register(ControlReg)
# admin.site.register(Risk)
admin.site.register(RiskReg)
admin.site.register(BusinessGroup)
admin.site.register(Business)