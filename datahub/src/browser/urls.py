# -*- coding: utf-8 -*-
from django.conf.urls import patterns, include, url
from django.views.generic.base import RedirectView
from views import OAuthAppUpdate


urlpatterns = patterns(
    '',

    # Home Page
    url(r'^$', 'browser.views.home', name='browser-home'),
    url(r'^about$', 'browser.views.about', name='browser-about'),
    url(r'^favicon\.ico$',
        RedirectView.as_view(url='/static/images/favicon.ico',
                             permanent=True)),

    # WWW Pages
    url(r'^www/', include('www.urls', namespace='www')),

    # Account Related
    url('', include('social.apps.django_app.urls', namespace='social')),
    url(r'^account/', include('account.urls')),


    # OAuth Provider
    # override the default app update form
    url(r'^oauth2/applications/(?P<pk>\d+)/update/$',
        OAuthAppUpdate.as_view(), name="update"),
    # override the default app listing page to use /developer/apps
    url(r'^oauth2/applications/$',
        RedirectView.as_view(pattern_name='browser-apps',
                             permanent=True), name="list"),
    url(r'^oauth2/', include('oauth2_provider.urls',
        namespace='oauth2_provider')),


    # API Pages
    url(r'^api/', include('api.urls', namespace='api')),
    url(r'^api-auth/', include('rest_framework.urls',
        namespace='rest_framework')),
    url(r'^api-docs/', include('rest_framework_swagger.urls')),

    # Thrift Services
    url(r'^service$', 'browser.views.service_core_binary',
        name='browser-thrift_service_binary'),
    url(r'^service/account$', 'browser.views.service_account_binary',
        name='browser-thrift_service_account'),
    url(r'^service/json$', 'browser.views.service_core_json',
        name='browser-thrift_service_json'),


    # Create
    url(r'^create/(\w+)/repo/?$', 'browser.views.repo_create',
        name='browser-repo_create'),
    url(r'^create/(\w+)/(\w+)/card/?$', 'browser.views.card_create',
        name='browser-card_create'),
    url(r'^create/annotation/?$', 'browser.views.create_annotation',
        name='browser-create_annotation'),
    
    ####add by beyhhhh>>>
    url(r'^browse/board/?$', 'browser.views.show_board',
        name='browser-show_board'),
    url(r'^browse/result_show/?$', 'browser.views.result_show',
        name='browser-result_show'),
    url(r'^browse/log_show/?$', 'browser.views.log_show',
        name='browser-log_show'),
    url(r'^browse/accuracy_show/?$', 'browser.views.accuracy_show',
        name='browser-accuracy_show'),
    #url(r'^browse/updata_record_result/?$', 'browser.views.updata_record_result',
    #    name='browser-log_show'),
    ####add by beyhhhh<<<
    # Browse
    url(r'^browse/(\w+)/(\w+)/table/(\w+)/?$', 'browser.views.table',
        name='browser-table'),
    url(r'^browse/(\w+)/(\w+)/query/?$', 'browser.views.query',
        name='browser-query'),
    url(r'^browse/(\w+)/(\w+)/card/(.+)/?$', 'browser.views.card',
        name='browser-card'),
    
    
    ##add by strongman
    
    
    
    url(r'^browse/(\w+)/(\w+)/?$', 'browser.views.repo',
        name='browser-repo'),
    #url(r'^browse/(\w+)/(\w+)/record/?$','browser.views.record',name='browser-record'),
    #url(r'^browse/(\w+)/(\w+)/tables/?$', 'browser.views.repo_tables',name='browser-repo_tables'),
    #url(r'^browse/(\w+)/(\w+)/files/?$', 'browser.views.repo_files',name='browser-repo_files'),
    
    ####>>add by beyhhhh
    ##url(r'^browse/(\w+)/(\w+)/codes/?$', 'browser.views.repo_codes',name='browser-repo_codes'),
    ####<<add by beyhhhh
    
    ##url(r'^browse/(\w+)/(\w+)/cards/?$', 'browser.views.repo_cards',name='browser-repo_cards'),
    
    
    
    ####>>add by beyhhhh
    #url(r'^browse/(\w+)/(\w+)/creat_new_codes/?$', 'browser.views.creat_new_codes',name='browser-creat_new'),
    
    #url(r'^browse/(\w+)/(\w+)/creat_new_data_sets/?$', 'browser.views.creat_new_data_sets',name='browser-creat_new'),
    
    #url(r'^browse/(\w+)/(\w+)/data_code_list_update/?$', 'browser.views.data_code_list_update',name='data_code_list_update'),
    
    #url(r'^browse/(\w+)/(\w+)/Push/?$', 'browser.views.data_code_list_update_github',name='data_code_list_update_github'),
    
    #url(r'^browse/(\w+)/(\w+)/update_file_flord_codes_data/?$', 'browser.views.update_file_flord_codes_data',name='browser-update_file_flord_codes_data'),
    
    #url(r'^browse/(\w+)/(\w+)/jupyter_coding/?$', 'browser.views.jupyter_coding',name='browser-creat_new'),
    
    url(r'^browse/(\w+)/(\w+)/upload_github/?$', 'browser.views.upload_github',name='browser-upload_github'),
    
    url(r'^browse/(\w+)/(\w+)/branch_list/?$', 'browser.views.code_branch_list',
        name='browser-branch_list'),
    
    
    url(r'^browse/(\w+)/(\w+)/(\w+)/commit/?$', 'browser.views.commit_code_watch',name='browser-commit_code_watch'),
    
    url(r'^browse/(\w+)/(\w+)/(\w+)/reset/?$', 'browser.views.reset_project_commit',name='browser-reset_project_commit'),
    
    url(r'^browse/(\w+)/(\w+)/(\w+)/(.+)/run/?$', 'browser.views.run_the_exp',name='browser-run_the_exp'),
    
    url(r'^browse/(\w+)/(\w+)/(.+)/table_show/?$', 'browser.views.table_show',name='browser-table_show'),
    
     url(r'^browse/(\w+)/(\w+)/(.+)/Make_data_set_public/?$', 'browser.views.Make_data_set_public',name='browser-Make_data_set_public'),
    
     url(r'^browse/(\w+)/(\w+)/(.+)/Make_code_public/?$', 'browser.views.Make_code_public',name='browser-Make_code_public'),
    ####<<add by beyhhhh
    

    ####add by beyhhhh>>>
    ####they are the url that add in twice change 
    
    url(r'^browse/(\w+)/add_to_the_repo/creat/?$', 'browser.views.add_to_the_repo', name='browser-add_to_the_repo'),
    
    
    url(r'^browse/public/data_set/?$', 'browser.views.public_data_set', name='browser-public_data_set'),
    
    
    url(r'^browse/(\w+)/(\w+)/add_codes/?$', 'browser.views.add_codes_to_repo',name='browser-add_codes_to_repo'),
    
    
    url(r'^browse/(\w+)/(\w+)/add_datas/?$', 'browser.views.add_datas_to_repo',name='browser-add_datas_to_repo'),
    
    url(r'^browse/(\w+)/(\w+)/move_code_to_repo/?$', 'browser.views.move_code_to_repo',name='browser-move_code_to_repo'),
    
    url(r'^browse/(\w+)/(\w+)/move_data_to_repo/?$', 'browser.views.move_data_to_repo',name='browser-move_data_to_repo'),
    
    ####<<<add by beyhhhh
    url(r'^browse/public/?$', 'browser.views.public_data_set', name='browser-public'),
    
    url(r'^browse/(\w+)/?$', 'browser.views.user', name='browser-user'),
    
    url(r'^browse/?$', 'browser.views.user', name='browser-user-default'),

    url(r'^browse/(\w+)/(\w+)/securitypolicies/(\w+)/?$',
        'browser.views.security_policies', name='browse-security_policies'),




    # Delete
    url(r'^delete/(\w+)/(\w+)/?$', 'browser.views.repo_delete',
        name='browser-repo_delete'),
    url(r'^delete/(\w+)/(\w+)/table/(\w+)/?$', 'browser.views.table_delete',
        name='browser-table_delete'),
    url(r'^delete/(\w+)/(\w+)/view/(\w+)/?$', 'browser.views.view_delete',
        name='browser-view_delete'),
    url(r'^delete/(\w+)/(\w+)/card/(\w+)/?$', 'browser.views.card_delete',
        name='browser-card_delete'),
    url(r'^delete/(\w+)/(\w+)/file/([ -~]+)/?$', 'browser.views.file_delete',
        name='browser-file_delete'),


    # Export
    url(r'^export/(\w+)/(\w+)/table/(\w+)/?$', 'browser.views.table_export',
        name='browser-table_export'),
    url(r'^export/(\w+)/(\w+)/card/(\w+)/?$', 'browser.views.card_export',
        name='browser-card_export'),


    # Special File Operations
    url(r'^upload/(\w+)/(\w+)/file/?$', 'browser.views.file_upload',
        name='browser-file_upload'),
    
    #add bey beyhhhh>>>
    url(r'^upload/(\w+)/(\w+)/code/?$', 'browser.views.code_upload',
        name='browser-code_upload'),
    
    url(r'^upload/(\w+)/(\w+)/data/?$', 'browser.views.data_upload',
        name='browser-data_upload'),
    #<<<add by beyhhhh
    
    url(r'^import/(\w+)/(\w+)/file/([ -~]+)', 'browser.views.file_import',
        name='browser-file_import'),
    url(r'^download/(\w+)/(\w+)/file/([ -~]+)', 'browser.views.file_download'),


    # Settings
    #url(r'^settings/(\w+)/(\w+)/?$','browser.views.repo_settings',name='browser-repo_settings'),


    # Collaborators
    # url(r'^collaborator/repo/(\w+)/(\w+)/add/?$','browser.views.repo_collaborators_add',name='browser-repo_collaborators_add'),

    #url(r'^collaborator/repo/(\w+)/(\w+)/remove/(\w+)/?$','browser.views.repo_collaborators_remove',name='browser-repo_collaborators_remove'),


    # Developer Apps
    url(r'^developer/apps/?$', 'browser.views.apps',
        name='browser-apps'),

    url(r'^developer/apps/detail/(\w+)/?$', 'browser.views.thrift_app_detail',
        name='browser-thrift_app_detail'),

    url(r'^developer/apps/register/?$', 'browser.views.app_register',
        name='browser-app_register'),

    url(r'^developer/apps/remove/(\w+)/?$', 'browser.views.app_remove',
        name='browser-app_remove'),


    # Permissions
    url(r'^permissions/apps/allow_access/(\w+)/(\w+)$',
        'browser.views.app_allow_access',
        name='browser-app_allow_access'),
    url(r'^update_visibility/(\w+)/(\w+)/card/(.+)/?$',
        'browser.views.card_update_public',
        name='browser-card_update_public'),


    # Security Policies
    url(r'^create/(\w+)/(\w+)/(\w+)/securitypolicy/?$',
        'browser.views.security_policy_create', name='security-policy_create'),
    url(r'^edit/(\w+)/(\w+)/(\w+)/securitypolicy/(\w+)/?$',
        'browser.views.security_policy_edit', name='security-policy_edit'),
    url(r'^delete/(\w+)/(\w+)/(\w+)/securitypolicy/(\w+)/?$',
        'browser.views.security_policy_delete',
        name='browser-securitypolicy_delete'),
    url(r'^execute/(\w+)/(\w+)/(\w+)/securitypolicy/query/?$',
        'browser.views.security_policy_query', name='security-policy_query'),



    # Client Apps
    url(r'^apps/console/', include('console.urls', namespace='console')),
    url(r'^apps/refiner/', include('refiner.urls', namespace='refiner')),
    url(r'^apps/dbwipes/', include('dbwipes.urls', namespace='dbwipes')),
    url(r'^apps/viz/', include('viz2.urls', namespace='viz2')),
    url(r'^apps/sentiment/', include('sentiment.urls', namespace='sentiment')),
    url(r'^apps/dataq/', include('dataq.urls', namespace='dataq')),
    url(r'^apps/datatables/', include('datatables.urls',
        namespace='datatables')),
)
