from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# Create your models here.

class Regulations(models.Model):
    regulation = models.TextField()
    description = models.TextField()
    link=models.TextField()
    content=models.TextField()
    objects = models.Manager() 
    def __str__(self):
        return self.regulation


class BusinessActivity(models.Model):
    businessdefinition_q = models.TextField()
    businessdefinition_a=models.TextField()
    jurisdiction=models.TextField()
    businessdefinition=models.TextField()    
    objects = models.Manager()
    

    def __str__(self):
        return self.businessdefinition_a

class Business(models.Model):
    businessactivity=models.TextField()
    user= models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE)
    status = models.CharField(max_length=10, default='pending')
    edit_status = models.CharField(max_length=10, default='pending')
    created_at = models.DateTimeField(default=timezone.now)
    objects = models.Manager()

    def __str__(self):
        return self.businessactivity

class BusinessGroup(models.Model):
      groupname = models.TextField()
      BusinessActivity = models.TextField()
      user= models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE)
      created_at = models.DateTimeField(default=timezone.now)
      objects = models.Manager()

      def __str__(self):
        return self.groupname

class BAReg(models.Model):
    regulation = models.TextField()
    status = models.CharField(max_length=10, default='pending')
    edit_status = models.CharField(max_length=10, default='pending')
    businessdefinition_q = models.TextField()
    businessdefinition_a=models.TextField()
    jurisdiction=models.TextField()
    user= models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now)
    category=models.TextField(default="Individual")
    objects = models.Manager()

    def __str__(self):
        return self.businessdefinition_a

class ProcessReg(models.Model):
    regulation = models.TextField()
    businessdefinition_q = models.TextField()
    businessdefinition_a=models.TextField()
    jurisdiction=models.TextField()
    process = models.TextField()
    description = models.TextField()
    status = models.CharField(max_length=10, default='pending')
    edit_status = models.CharField(max_length=10, default='pending')
    user= models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now)
    category=models.TextField(default='Individual')
    objects = models.Manager()
    def __str__(self):
        return self.businessdefinition_a

class Policy(models.Model):
    policy = models.TextField()
    description = models.TextField()
    user= models.ForeignKey(User, on_delete=models.CASCADE)
    objects = models.Manager()
    created_at = models.DateTimeField(default=timezone.now)
    def __str__(self):
        return self.policy

class Controls(models.Model):
    control = models.TextField()
    description = models.TextField()
    content=models.TextField()
    user= models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now)
    objects = models.Manager()

    def __str__(self):
        return self.control

class ControlReg(models.Model):
    regulation = models.TextField()
    businessdefinition_q = models.TextField()
    businessdefinition_a=models.TextField()
    jurisdiction=models.TextField()
    process = models.TextField()
    description = models.TextField()
    controlarea = models.TextField()
    controlobjective = models.TextField()
    controldescription=models.TextField()
    status = models.CharField(max_length=10,default='pending')
    edit_status = models.CharField(max_length=10,default='pending')
    user= models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now)
    category=models.TextField(default='Individual')
    objects = models.Manager()
    def __str__(self):
        return self.businessdefinition_a

class Risk(models.Model):
    risk = models.TextField()
    comment = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    objects = models.Manager() 
    def __str__(self):
        return self.risk

class RiskReg(models.Model):
    regulation = models.TextField()
    businessdefinition_q = models.TextField()
    businessdefinition_a=models.TextField()
    jurisdiction=models.TextField()
    process = models.TextField()
    description = models.TextField()
    controlarea = models.TextField()
    controlobjective = models.TextField()
    controldescription=models.TextField()
    status = models.CharField(max_length=10,default='pending')
    edit_status = models.CharField(max_length=10,default='pending')
    user= models.ForeignKey(User, on_delete=models.CASCADE)
    risk = models.TextField()
    comment=models.TextField()
    riskdescription=models.TextField(default='NA')
    created_at = models.DateTimeField(default=timezone.now)
    category=models.TextField(default='Individual')
    objects = models.Manager() 
    def __str__(self):
        return self.businessdefinition_a


