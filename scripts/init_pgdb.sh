DB_NAME=chequer_db
DB_USER=chequer_admin_client
DB_PASS=chequer_admin_client_secret

# create user with password
sudo -u postgres psql -c "CREATE USER $DB_USER WITH PASSWORD '$DB_PASS';"

# create database with owner
sudo -u postgres psql -c "CREATE DATABASE $DB_NAME WITH OWNER $DB_USER ENCODING 'UTF8';"