set -x #echo on
curl -L -O https://github.com/Yossi/omer/archive/pythonanywhere.zip
unzip pythonanywhere.zip
mv omer-pythonanywhere omer
mv omer/deploy.sh deploy.sh
rm pythonanywhere.zip
cd omer
source virtualenvwrapper.sh
workon omer
pip install -U -r requirements.txt
pip list --outdated --format=columns