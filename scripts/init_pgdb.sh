# create user ayush_admin_client
sudo psql -U postgres -c "CREATE USER chequer_admin_client WITH PASSWORD 'chequer_admin_client_secret';"
# create database ayush_connect with owner ayush_admin_client and encoding UTF8
sudo psql -U postgres -c "CREATE DATABASE chequer_db WITH OWNER chequer_admin_client ENCODING 'UTF8';"