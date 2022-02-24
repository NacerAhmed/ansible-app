from .views import *
from django.urls import path

urlpatterns = [
    path('',index,name='home'),
    path('setup',setup,name='setup'),
    path('setup/add-playbook',add_playbook,name='add_playbook'),
    path('login',login,name='login'),
    path('logout',logout,name='logout'),
    path('register', register, name='register' ),
    path('users', users, name='users' ),
    path('user/edit-account/<int:account_id>', edit_account, name='edit_account' ),
    path('users/add-user', add_user, name='add_user' ),
    path('servers', servers, name='servers' ),
    path('groups', groups, name='groups' ),
    path('access', access, name='access' ),
    path('access/add-user-access', create_user_access, name='add_user_access' ),
    path('servers/addserver', addserver, name='addserver' ),
    path('servers/delete-server/<int:server_id>', delete_server, name='delete_server' ),
    path('servers/ping-ssh-test', ping_ssh_test, name='pingssh' ),
    path('servers/server/update-status/<int:server_id>', update_status, name='update_status'),
    path('servers/server/install_pachakge/httpd/<int:server_id>', install_httpd, name='install_httpd'),
    path('servers/server/install_pachakge/php/<int:server_id>', install_php, name='install_php'),
    path('servers/server/install_pachakge/mariadb/<int:server_id>', install_mariadb, name='install_mariadb'), 
    path('servers/server/install_pachakge/git/<int:server_id>', install_git, name='install_git'), 


]
