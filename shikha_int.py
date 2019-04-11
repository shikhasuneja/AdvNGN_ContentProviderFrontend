from populatedb_api import populate_db as pb

admin_user_email="shikha.90145@gmail.com"
user_to_be_added="shikha"
index_file="index_v1.html"

a1=pb()
a1.api_account(admin_user_email)
--- new url creation -- nws_customers.json, redundancy.json

a1.api_account_users(admin_user_email,user_to_be_added)
--- user addition, users.json, nws_customers.json

a1.api_cp_content(admin_user_email,index_file)
--- new index (intial + new), index_file, nws_customers.json

a1.api_version(admin_user_email)
--- new + revert (webpage_version.json)
