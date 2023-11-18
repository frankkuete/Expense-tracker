echo 'activate the python virtual environment...'
source env/Scripts/activate
echo 'installing the dependencies...'
pip install -r requirements.txt
echo 'Create the database..'
python ./create_database.py
echo 'Startup the app'
python run.py
deactivate
echo 'Script is Done_'