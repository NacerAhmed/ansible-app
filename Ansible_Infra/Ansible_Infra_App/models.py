from django.db import models
from django.contrib.auth.models import User,Group

class Server(models.Model):
    name = models.CharField(max_length=50)
    ip = models.CharField(max_length=50)
    superuser_name = models.CharField(max_length=50)
    superuser_password = models.CharField(max_length=512)
    group = models.CharField(max_length=50)
    status= models.CharField(max_length=50)
    master= models.BooleanField(default=False)
    
    def set_status(self, status):
         self.status = status

class Access(models.Model):
    server = models.ForeignKey(Server, on_delete=models.CASCADE)
    group= models.ForeignKey(Group, on_delete=models.CASCADE)
    login= models.CharField(max_length=50)
    name= models.CharField(max_length=50)
    description= models.CharField(max_length=50)
    password= models.CharField(max_length=200)
    status= models.CharField(max_length=50)

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar=models.ImageField(upload_to="avatars/", default=None)


class Setup(models.Model):
    master = models.ForeignKey(Server, on_delete=models.CASCADE)
    inventory= models.CharField(max_length=150)
    config= models.CharField(max_length=150)
    status=models.CharField(max_length=150)
    backup_directory=models.CharField(max_length=150)
    palybooks_directory=models.CharField(max_length=150)
    play_rem_dir=models.CharField(max_length=150)
    exec_play_rem_dir=models.CharField(max_length=150)
    

class Playbook(models.Model):
    name = models.ForeignKey(Server, on_delete=models.CASCADE)
    desc= models.CharField(max_length=150)
    
    
class Package(models.Model):
    playbook = models.ForeignKey(Playbook, on_delete=models.CASCADE)
    name= models.CharField(max_length=150)
    desc= models.CharField(max_length=150)
    is_installed = models.BooleanField(default=False)
    
    

       

Group.add_to_class('description', models.CharField(max_length=180,null=True, blank=True))
User.add_to_class('poste', models.CharField(max_length=180,null=True, blank=True))
User.add_to_class('tel', models.CharField(max_length=180,null=True, blank=True))