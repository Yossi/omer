curl -L -O https://github.com/Yossi/omer/archive/pythonanywhere.zip
unzip pythonanywhere.zip
rm pythonanywhere.zip
rm -rf omer
mv omer-pythonanywhere omer
mv omer/deploy.sh deploy.sh
cd omer
source virtualenvwrapper.sh
workon omer
pip install -U -r requirements.txt
pip list --outdated --format=columns
rm -rf .cache
rm omer/.gitignore
rm omer/requirements.txt
