from django.shortcuts import render,redirect
from django.contrib.auth.models import User, auth, Group
from .models import Access, Server, Setup
from django.shortcuts import render , redirect
from django.contrib import messages
import paramiko
from .models import Profile
from django.contrib.auth import logout as auth_logout
import socket
import os
from django.db.models import Q
import fileinput
import subprocess
import sys







def index(request):
    if request.user.is_authenticated:
        profiles=Profile.objects.all()
        if request.user.is_superuser == True:
            profile=Profile.objects.get(user_id=request.user.id)
           
            servers=Server.objects.all()
            users=User.objects.all()
            access=Access.objects.all()
            users=User.objects.filter(~Q(is_superuser= True))
            setup=Setup.objects.all()
            groups=Group.objects.all()
            
            user_group_count={}
            group_list_servers={}
            
            for group in groups:
               
                list_users=User.objects.filter(groups__name=group.name, is_superuser=False)                   
                list_servers=Server.objects.filter(group=group.name) 
                user_group_count[group.id]=list_users.count()
                group_list_servers[group.id]=list_servers.count()
                
            setup_exist=Setup.objects.all().count()
            if setup_exist >0:
               setup_status= setup[0].status
            else:
                setup_status='failed'
                
            actif_servers=Server.objects.filter(status='Connected')
            ssh_failed=Server.objects.filter(status='SSH Failed')
            login_failed_servers=Server.objects.filter(status='Invalid Username/Password')
            context={'group_list_servers':group_list_servers, 'user_group_count':user_group_count, 'groups':groups, 'profiles':profiles, 'users':users, 'setup_status':setup_status, 'access':access, 'users':users, 'profile':profile,'actif_servers':actif_servers,'login_failed_servers':login_failed_servers,'ssh_failed':ssh_failed,'servers':servers}
            return render(request, 'dist/index.html',context)
        else:
            
            profile=Profile.objects.get(user_id=request.user.id)
            user_group=request.user.groups.get(user=request.user)
            
            servers=Server.objects.filter(group=user_group.name)
            users= User.objects.filter(groups__name=user_group.name)
           

            access=Access.objects.filter(group=user_group).order_by('name') 
            
            actif_servers=Server.objects.filter(group=user_group.name,status='Connected')
            ssh_failed=Server.objects.filter(group=user_group.name,status='SSH Failed')
            login_failed_servers=Server.objects.filter(group=user_group.name,status='Invalid Username/Password')
            context={'profiles':profiles,'users':users, 'user_group':user_group, 'access':access, 'users':users, 'profile':profile,'actif_servers':actif_servers,'login_failed_servers':login_failed_servers,'ssh_failed':ssh_failed,'servers':servers}
            return render(request, 'dist/index.html',context)
    
    else:
        return redirect("login")
        
    
    

def login(request):
    if  request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = auth.authenticate(username = username, password =password  )
        
        if user is not None:
            auth.login(request , user)
            return redirect('home')    
        else:
            messages.info(request, 'invalid username or password')
            context={'error':'true'}
            return render (request,'dist/authentication/layouts/aside/sign-in.html', context)
    else:
        context={'error':'false'}
        return render (request,'dist/authentication/layouts/aside/sign-in.html',context)
    

def register(request):
    if  request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        email = request.POST['email']
        username = request.POST['username']
        password= request.POST['password'] 
        last_name = request.POST['last_name']
        user = User.objects.create_user(first_name=first_name, last_name=last_name, username = username , password = password , email = email)
        user.save()
        auth.login(request , user)
        return redirect('home')
    else:
        return render (request,'dist/authentication/layouts/aside/sign-up.html')
    
    
def users(request):
    
    if  request.user.is_authenticated:
        
        if request.user.is_superuser==True:
            list_users=User.objects.all()
            profiles=Profile.objects.all()
            actif_users=User.objects.filter(is_active=True)
            inactif_users=User.objects.filter(is_active=False)
            rest=User.objects.all().count()-10
            profile_avatar=Profile.objects.get(user_id=request.user.id)
            context={'profile_avatar':profile_avatar, 'rest':rest, 'list_users':list_users,'profiles':profiles, 'actif_users':actif_users,'inactif_users':inactif_users}
            return render (request,'dist/widgets/users.html',context)
            
        else:
            user_group=request.user.groups.get(user=request.user)
            list_users=User.objects.filter(groups__name=user_group.name)
            profiles=Profile.objects.all()
            actif_users=User.objects.filter(groups__name=user_group.name,is_active=True)
            inactif_users=User.objects.filter(groups__name=user_group.name,is_active=False)
            profile_avatar=Profile.objects.get(user_id=request.user.id)
            context={'profile_avatar':profile_avatar,'list_users':list_users,'profiles':profiles, 'actif_users':actif_users,'inactif_users':inactif_users}
            return render (request,'dist/widgets/users.html',context)
    else:
        return redirect('login')


def edit_account(request,account_id):
    
    if  request.user.is_authenticated:
        user=User.objects.get(id=account_id)
        
        if request.method == 'POST' and 'update_user' in request.POST:
            
            first_name = request.POST['fname']
            last_name = request.POST['lname']
            email = request.POST['email']
            phone = request.POST['phone']
            job_title = request.POST['job_title']
            user_group = request.POST['group']
            usertype = request.POST['usertype']
        
            if  request.FILES.get('avatar'):
                profile=Profile.objects.get(user_id=user.id)
                profile.avatar=request.FILES['avatar']
                profile.save()
            
            user.first_name=first_name
            user.last_name=last_name
            user.email=email
            user.tel=phone
            user.poste=job_title
            user.is_super_user=usertype
            
            user.groups.clear()
            group=Group.objects.get(name=user_group)
            group.user_set.add(user)
            user.save()

        if request.method == 'POST' and 'desactive_user' in request.POST:
            user.is_active=False
            user.save()
            
        if request.method == 'POST' and 'reactive_user' in request.POST:
            user.is_active=True
            user.save()  
        
        if request.method == 'POST' and 'update_pass' in request.POST:
            password = request.POST['currentpassword']
            newpassword = request.POST['newpassword']
            user.set_password(newpassword)
            user.save() 
           
        
        user_account=User.objects.filter(id=account_id)
        if user_account.count() >0:

            user_account=user_account[0]
            profile_avatar=Profile.objects.get(user_id=request.user.id)
            user_profile_avatar=Profile.objects.get(user_id=account_id)
            groups=Group.objects.all()
            context={'groups':groups, 'user_account':user_account, 'user_profile_avatar':user_profile_avatar, 'profile_avatar':profile_avatar}
            return render (request,'dist/widgets/edit-account.html',context)
        else:
            return redirect('home') 
    else:
        return redirect('login')








def logout(request):
    auth_logout(request)
    return redirect('login')



def add_user(request):
    if request.user.is_authenticated:
        groups=Group.objects.all()
        profile_avatar=Profile.objects.get(user_id=request.user.id)
        if request.method == 'POST':
            fname = request.POST['fname']
            lname = request.POST['lname']
            email = request.POST['email']
            group = request.POST['group']
            usertype = request.POST['usertype']
            alllogin=request.POST['alllogin']
            username = request.POST['username']
            password= request.POST['password']
            avatar= request.FILES['avatar']
            phone= request.POST['phone']
            job_title= request.POST['job_title']
            
            if usertype=='simple':
                is_superuser=False
            else:
                is_superuser=True
            
            if alllogin=='off':
                is_active=False
            else:
                is_active=True
             
            user = User.objects.create_user(first_name=fname, is_active=is_active, is_superuser=is_superuser, poste=job_title, tel=phone,last_name=lname, username = username , password = password , email = email)  
            profile=Profile(avatar=avatar ,user=user)
            last_avatar=profile.avatar    
            profile.save()
            usergroup=Group.objects.get(name = group)       
            usergroup.user_set.add(user)
            
            context={'status':'user added','last_avatar':last_avatar}
            return render (request,'dist/account/settings.html',context) 
        
        context={'groups':groups,'profile_avatar':profile_avatar}
        return render (request,'dist/account/settings.html',context)         
    else:  
        return redirect('login')       
            
    
    
    
    


def servers(request):
    
    if  request.user.is_authenticated:
        profile=Profile.objects.get(user_id=request.user.id)
        
        
        if request.user.is_superuser==True:
            list_servers=Server.objects.all().order_by('-master')
            actif_servers=Server.objects.filter(status='Connected').count()
            inactif_servers=Server.objects.filter(~Q(status= 'Connected')).count()
            context={"profile_avatar":profile, "servers":list_servers,'actif_servers':actif_servers,'inactif_servers':inactif_servers}
        else:
            user_group=request.user.groups.get(user=request.user)
            actif_servers=Server.objects.filter(status='Connected', group =user_group).count()
            inactif_servers=Server.objects.filter(~Q(status= 'Connected'),group =user_group).count()
            
            list_servers=Server.objects.filter(group=user_group).order_by('-master')        
            context={"profile_avatar":profile, "servers":list_servers,'actif_servers':actif_servers,'inactif_servers':inactif_servers}
        return render (request,'dist/widgets/tables.html',context)
    else:
        return redirect('login')

def access(request):
    
    if  request.user.is_authenticated:
        profile_avatar=Profile.objects.get(user_id=request.user.id)

        if request.user.is_superuser==True:
            list_access=Access.objects.all()
            servers=Server.objects.all()
            enabled_access=Access.objects.filter(status='actif').count()
            disabled_access=Access.objects.filter(status='inactif').count()
        else:
            user_group=request.user.groups.get(user=request.user)
            list_access=Access.objects.filter(group=user_group).order_by('name') 
            servers=Server.objects.filter(group=user_group).order_by('name') 
            enabled_access=Access.objects.filter(status='actif',group =user_group).count()
            disabled_access=Access.objects.filter(status='inactif',group =user_group).count()
        
        context={'profile_avatar':profile_avatar, "list_access":list_access,'servers':servers,'enabled_access':enabled_access,'disabled_access':disabled_access}
        return render (request,'dist/widgets/access.html',context)
    else:
        return redirect('login')


def addserver(request):
    if request.user.is_authenticated:
        
        if request.user.is_superuser == True:
            profile_avatar=Profile.objects.get(user_id=request.user.id)
            groups=Group.objects.all()
        
            if request.method == 'POST':
                setup=Setup.objects.get(status='completed')
                inventory=setup.inventory
                backup_dir=setup.backup_directory
                
                name = request.POST['server_name']
                group = request.POST['group']
                server_ip = request.POST['server_ip']
                superuser_name = request.POST['superuser_name']
                master = request.POST['master']
                superuser_password = request.POST['superuser_password']
                status=servertest(server_ip,superuser_name,superuser_password)
                
                if master=='True':
                    master_server=Server.objects.filter(master=True)
                    if master_server.exists():
                        context={"status":"master exist",'profile_avatar':profile_avatar}
                        return render (request,'dist/utilities/wizards/vertical.html',context)
                    else:
                        server = Server(name=name, group=group, ip = server_ip , status=status, master=master, superuser_name = superuser_name , superuser_password = superuser_password)
                        server.save()
                        
                        context={"status":"master added",'profile_avatar':profile_avatar}
                        return render (request,'dist/utilities/wizards/vertical.html',context)

                
                master_server=Server.objects.get(master=True)  
                if status == "Connected":
                
            
                    
                    t = paramiko.Transport((master_server.ip, 22))
                    t.connect(username=master_server.superuser_name, password=master_server.superuser_password)
                    sftp = paramiko.SFTPClient.from_transport(t)
                    sftp.get(inventory,os.path.abspath(backup_dir)+'\inventory.txt')                    
  
                    
                    with open(os.path.join(backup_dir, 'inventory.txt')) as f,open(os.path.join(backup_dir, 'inventory2.txt'),"w") as out:
                        lines = f.readlines()
                        print (lines)
                        for ind,line in enumerate(lines):
                            if line.strip().startswith('['+ group +']'):
                                lines[ind] = (line+"     "+'\n'+ server_ip + '  ansible_ssh_user='+superuser_name+' ansible_ssh_pass='+superuser_password+' ansible_sudo_pass='+superuser_password+'\n')
                                break
                        for line in lines:
                            out.write(line)
                        
                    os.remove(os.path.join(backup_dir, 'inventory.txt'))
                    os.rename(os.path.join(backup_dir, 'inventory2.txt'), os.path.join(backup_dir, 'inventory.txt') )
                
                    t = paramiko.Transport((master_server.ip, 22))
                    t.connect(username=master_server.superuser_name, password=master_server.superuser_password)
                    sftp = paramiko.SFTPClient.from_transport(t)
                    
                    sftp.put(backup_dir+'/inventory.txt',inventory) 
                    
                  

                    server = Server(name=name, group=group, ip = server_ip , status=status, master=master, superuser_name = superuser_name , superuser_password = superuser_password)
                    server.save()
                    

                
                    context={"status":"login passed",'profile_avatar':profile_avatar}
                    return render (request,'dist/utilities/wizards/vertical.html',context)
                
                elif status == "Invalid Username/Password":
                    context={"status":"login failed",'profile_avatar':profile_avatar}
                    return render (request,'dist/utilities/wizards/vertical.html',context)
                else:
                    context={"status":"ssh failed",'profile_avatar':profile_avatar}
                    return render (request,'dist/utilities/wizards/vertical.html',context)
        else:
            return redirect('servers')    
        context={'groups':groups,'profile_avatar':profile_avatar}        
        return render (request,'dist/utilities/wizards/vertical.html',context)
    
    else:
        return redirect('home')
    
def servertest(address,username,password):
    s = socket.socket()
    port=22
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    s.settimeout(1)
    try:
        s.connect((address, port))
        try:
            ssh.connect(address, port, username, password)
            status="Connected"
        except Exception as e:
            status="Invalid Username/Password"
    except Exception as e:
        status="SSH Failed"
    finally:
        s.close()
    return status



def create_user_access(request):
    
    if request.user.is_authenticated:
        if request.user.is_superuser == True:
            profile_avatar=Profile.objects.get(user_id=request.user.id)
            servers=Server.objects.all()
            groups=request.user.groups.all()
            context={'servers':servers,'groups':groups,'profile_avatar':profile_avatar}
            if request.method == 'POST':
                
                master_server=Server.objects.get(master=True)
                setup=Setup.objects.get(master_id=master_server.id)
                inventory=setup.inventory
                backup_dir=setup.backup_directory
                playbook_dir=setup.play_rem_dir
                exec_playbook_dir=setup.exec_play_rem_dir
                status=servertest(master_server.ip, master_server.superuser_name, master_server.superuser_password)
               
                name=request.POST['name']
                desc=request.POST['desc']
                username=request.POST['username']
                password=request.POST['password']
                user_status=request.POST['access_status']
                access_type=request.POST['access_type']
                hostid=request.POST['host']
                
                if access_type == 'one':
                    server=Server.objects.get(id=hostid)
                    group=server.group
                else:
                    group = request.POST['group']


                
                if user_status =='on':
                    access_status='actif'
                    var_status='present'
                else:
                    access_status='inactif'
                    var_status='absent'
                    
                if status == "Connected":
                    
                    port=22
                    ssh = paramiko.SSHClient()
                    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                    ssh.connect(master_server.ip, port, master_server.superuser_name, master_server.superuser_password)
                

                    t = paramiko.Transport((master_server.ip, port))
                    t.connect(username=master_server.superuser_name, password=master_server.superuser_password)
                    sftp = paramiko.SFTPClient.from_transport(t)
                    sftp.get(playbook_dir+'/Playbook_create_user.yml',os.path.abspath(backup_dir)+'/Playbook_create_user.yml')   
                        
                
                    
                    with fileinput.FileInput(backup_dir+'/Playbook_create_user.yml', inplace=True,) as file:
                        for line in file:
                            print(line.replace("var_group",group), end='')
                
                    with fileinput.FileInput(backup_dir+'/Playbook_create_user.yml', inplace=True,) as file:
                        for line in file:
                            print(line.replace("var_username",username), end='')
                            
                    with fileinput.FileInput(backup_dir+'/Playbook_create_user.yml', inplace=True,) as file:
                        for line in file:
                            print(line.replace("var_password",password), end='')

                    with fileinput.FileInput(backup_dir+'/Playbook_create_user.yml', inplace=True, backup='.yml') as file:
                        for line in file:
                            print(line.replace("var_status",var_status), end='')

                    if access_type =='group':
                        servers=Server.objects.filter(group=group)
                        server_group=Group.objects.get(name=group)
                        for server in servers:
                            if server.master != True:
                                access=Access(login=username,password=password, status=access_status, server_id=server.id,group_id=server_group.id, name=name, description=desc)
                                access.save()
                    else:
                        server=Server.objects.get(id=hostid)
                        group=Group.objects.get(name=server.group)
                        access=Access(login=username,password=password, status=access_status, server_id=server.id,group_id=group.id, name=name, description=desc)
                        access.save()
                

          
                    ssh.close()
                    
                  

                   
                    dest=exec_playbook_dir
                    source=backup_dir+'/Playbook_create_user.yml'
                   
                    t = paramiko.Transport((master_server.ip, port))
                    t.connect(username=master_server.superuser_name, password=master_server.superuser_password)
                    sftp = paramiko.SFTPClient.from_transport(t)
                    sftp.put(source, dest+ "/Executed_Playbook_create_user.yml" )
                    
                    
                   
                   
                    if access_type == 'one':
                        server=Server.objects.get(id=hostid)
                        serer_ip=server.ip
                        ansible_playbook_command = 'ansible-playbook '+exec_playbook_dir+'/Executed_Playbook_create_user.yml -i '+inventory+' --limit '+serer_ip 
                    else:
                       
                        ansible_playbook_command = 'ansible-playbook '+exec_playbook_dir+'/Executed_Playbook_create_user.yml -i '+inventory+' --limit '+group 


                    ssh=paramiko.SSHClient()
                    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                    ssh.connect(master_server.ip,port,master_server.superuser_name,master_server.superuser_password)
                    stdin,stdout,stderr=ssh.exec_command(ansible_playbook_command)
                    error=stderr.readlines()
                    result=stdout.readlines()    
                        
                    ssh.close()
                    context={'error':error,'result':result,'profile_avatar':profile_avatar}
                    return render (request,'dist/widgets/add-server-user.html',context)
              
                    

        
                
                return render (request,'dist/widgets/add-server-user.html',context)
        
        
                
            return render (request,'dist/widgets/add-server-user.html',context)
        else:
            return redirect('access')
    else:
        return redirect('home')

    




def ping_ssh_test(request):
    if request.user.is_authenticated:
        profile_avatar=Profile.objects.get(user_id=request.user.id)
        if request.method == 'POST':
             server_ip = request.POST['server_ip']
             superuser_name = request.POST['superuser_name']
             superuser_password = request.POST['superuser_password']
             port=int(request.POST['port'])
             test_type=request.POST['type']
             s = socket.socket()
             s.settimeout(1)
             ssh = paramiko.SSHClient()
             ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
             if test_type=='ping':
                 try:
                     s.connect((server_ip, port))
                     context={'status':"p_p",'profile_avatar':profile_avatar}
                 except Exception as e:
                     context={'status':"p_f",'profile_avatar':profile_avatar}
                                         
             else:
                 try:
                     s.connect((server_ip, port))
                     try:
                         ssh.connect(server_ip, port, superuser_name, superuser_password)
                         context={'status':"l_p",'profile_avatar':profile_avatar}
                         
                     except Exception as e:
                         context={'status':"i_u_p",'profile_avatar':profile_avatar}
                         
                 except Exception as e:
                     context={'status':"s_f",'profile_avatar':profile_avatar}
                     
            
                 finally:
                     s.close()
        else:
            context={'status':'','profile_avatar':profile_avatar} 
    return render (request,'dist/widgets/ping-ssh.html',context)



def update_status(request,server_id):
    if request.user.is_authenticated:
        server=Server.objects.get(pk=server_id)
        s = socket.socket()
        s.settimeout(1)
        port=22
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            s.connect((server.ip, port))
            try:
                ssh.connect(server.ip, port, server.superuser_name, server.superuser_password)
                status="Connected"
                server.set_status(status)
                server.save()
            except Exception as e:
                status="Invalid Username/Password"
                server.set_status(status)
                server.save()
        except Exception as e:
            status="SSH Failed"
            server.set_status(status)
            server.save()
        finally:
            s.close()
    return redirect('servers')


def delete_server(request,server_id):
    if request.user.is_authenticated:
        if request.user.is_superuser == True:
            setup=Setup.objects.get(status='completed')
            inventory=setup.inventory
            backup_dir=setup.backup_directory
            server=Server.objects.get(pk=server_id)
            server.delete()
            
            master_server=Server.objects.get(master=True)  
            port=22
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(master_server.ip, port, master_server.superuser_name, master_server.superuser_password)
                    
            
            t = paramiko.Transport((master_server.ip, port))
            t.connect(username=master_server.superuser_name, password=master_server.superuser_password)
            sftp = paramiko.SFTPClient.from_transport(t)
            sftp.get(inventory,os.path.abspath(backup_dir)+'\inventory.txt')    
                
            
            
           
                            
        
                
            with open(os.path.join(backup_dir, 'inventory.txt'), "rt") as f:
                lines = f.readlines()
                
            with open(os.path.join(backup_dir, 'inventory.txt'), "wt") as f:
                for line in lines:
                    if not line.startswith(server.ip):
                        if not line.isspace():
                            f.write(line)
                        
            dest=inventory
            source=os.path.join(backup_dir, 'inventory.txt')
                   
            t = paramiko.Transport((master_server.ip, port))
            t.connect(username=master_server.superuser_name, password=master_server.superuser_password)
            sftp = paramiko.SFTPClient.from_transport(t)
            sftp.put(source, dest)            
                        
                
            return redirect('servers')
       
        else:
            return redirect('servers')
   
    else:
        return redirect('home')


def auto_update_status():
    
        servers=Server.objects.all()
        s = socket.socket()
        s.settimeout(1)
        port=22
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        for server in servers:
            try:
                s.connect((server.ip, port))
                try:
                    ssh.connect(server.ip, port, server.superuser_name, server.superuser_password)
                    status="Connected"
                    server.set_status(status)
                    server.save()
                except Exception as e:
                    status="Invalid Username/Password"
                    server.set_status(status)
                    server.save()
            except Exception as e:
                status="SSH Failed"
                server.set_status(status)
                server.save()
            finally:
                s.close()


def setup(request):
     if request.user.is_authenticated:
         
        if request.user.is_superuser == True:
            profile=Profile.objects.get(user_id=request.user.id)
            setup=Setup.objects.all()
            if setup:
                master=Server.objects.get(master=True)
                if master:
                    setup=setup[0]
                    setup_status=setup.status
                    if setup_status == 'completed':   
                        status=100
                        exist=1
                        setup_complete=100
                        context={'setup':setup, 'master':master, 'profile':profile, 'exist':exist,'setup_complete':setup_complete,'setup_status':setup_status}
         
                    else:
                        status=50
                        exist=1
                        setup_complete=50
                        context={'setup':setup, 'master':master, 'profile':profile, 'exist':exist,'setup_complete':setup_complete,'setup_status':setup_status}

                else:
                    status=0
                    exist=0
                    setup_complete=0
                    setup_status='failed'
                    context={'setup':setup,'profile':profile, 'exist':exist,'setup_complete':setup_complete,'setup_status':setup_status}

            else:
                status=0
                exist=0
                setup_complete=0
                setup_status='failed'
                context={'profile':profile, 'exist':exist,'setup_complete':setup_complete,'setup_status':setup_status}

                 
            if request.method == 'POST' and 'save_master' in request.POST:
                name = request.POST['server_name']
                group = 'admin'
                server_ip = request.POST['server_ip']
                superuser_name = request.POST['superuser_name']
                master = True
                superuser_password = request.POST['superuser_password']
                status=servertest(server_ip,superuser_name,superuser_password)
                    
                    
                    
                if status == "Connected":
                    server = Server(name=name, group=group, ip = server_ip , status=status, master=master, superuser_name = superuser_name , superuser_password = superuser_password)
                    server.save()
                    setup=Setup(master=server,status='almost')
                    setup.save()
                        
                        
                    return redirect('setup')
                
                
                   
            if request.method == 'POST' and 'files_path' in request.POST:
                inventory = request.POST['inventory']
                config =request.POST['config']
                backup =request.POST['backup']
                playbooks =request.POST['playbooks']
                play_rem_dir=request.POST['play_rem_dir']
                exec_play_rem_dir=request.POST['exec_play_rem_dir']
                    
                master=Server.objects.get(master=True)
                if master:
                    status=servertest(master.ip,master.superuser_name,master.superuser_password)
                        
                    if status == "Connected":
                        setup=Setup.objects.get(master_id=master.id)
                        setup.inventory=inventory
                        setup.config=config
                        status='completed'
                        setup.status=status
                        setup.play_rem_dir=play_rem_dir
                        setup.exec_play_rem_dir=exec_play_rem_dir
                        setup.backup_directory=backup.replace("\\" ,"/")
                        palybooks_directory=playbooks.replace("\\" ,"/")
                        setup.palybooks_directory=palybooks_directory
                        setup.save()
                        
                        port=22
                        ssh = paramiko.SSHClient()
                        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                        ssh.connect(master.ip, port, master.superuser_name, master.superuser_password)
                        
                        command= ('mkdir '+play_rem_dir)
                        ssh.exec_command(command,get_pty=True)
                        
                        command= ('mkdir '+exec_play_rem_dir)
                        ssh.exec_command(command,get_pty=True)
                    
                        files = os.listdir(os.path.abspath(palybooks_directory))
                        for file in files:
                            try:
                                
                                t = paramiko.Transport((master.ip,port ))
                                t.connect(username=master.superuser_name, password=master.superuser_password)
                                sftp = paramiko.SFTPClient.from_transport(t)
                                sftp.put(os.path.join(os.path.abspath(palybooks_directory), file), play_rem_dir + "/" + file)
                            finally:
                                t.close()
                        return redirect('setup')
                else:
                    return render (request,'dist/widgets/setup.html',context)
                    
                return render (request,'dist/widgets/setup.html',context)   
                
                
  
           
            return render (request,'dist/widgets/setup.html',context)
        else:
            return redirect('home')





def add_playbook(request):
    if request.user.is_authenticated:
        profile=Profile.objects.get(user_id=request.user.id)
        setup=Setup.objects.all()
        setup_exist=setup.count()
        if setup_exist !=0 :
            status=setup[0].status
        else:
            status='failed'
            
        if request.method == 'POST':
            file = request.FILES['file']
            file_name = request.POST['file_name']
            master=Server.objects.get(master=True)
            
            if master:
                setup=Setup.objects.get(master_id=master.id)
             
            
            port=22
            t = paramiko.Transport((master.ip,port ))
            t.connect(username=master.superuser_name, password=master.superuser_password)
            sftp = paramiko.SFTPClient.from_transport(t)
            sftp.put(os.path.join(os.path.abspath(setup.palybooks_directory), file_name), setup.play_rem_dir + "/" + file_name)
            
            send_msg='success'
            context={'profile':profile,'status':status,'send_msg':send_msg}
            return render (request,'dist/widgets/add-playbook.html',context)
        
        context={'profile':profile,'status':status}
        return render (request,'dist/widgets/add-playbook.html',context)
    
    return redirect('home')