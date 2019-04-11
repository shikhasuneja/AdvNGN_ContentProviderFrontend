from populatedb_api import populate_db as pb

admin_user_email="shikha.90145@gmail.com"
user_to_be_added="shikha"
index_file="index_v1.html"

a1=pb()
a1.api_account(admin_user_email)
a1.api_cp_content(admin_user_email,index_file)
a1.api_account_users(admin_user_email,user_to_be_added)
a1.api_version(admin_user_email)
