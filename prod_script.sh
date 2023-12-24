echo 'installing the dependencies...'
pip install -r requirements.txt
echo 'Create the database..'
python ./create_database.py
echo 'Startup the app...'