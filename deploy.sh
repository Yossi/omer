# manually set up a virtualenv on pythonanywhere
# mkvirtualenv omer --python=/usr/bin/python3.10
# also point the web tab at this after

echo Downloading https://github.com/Yossi/omer/archive/pythonanywhere.zip
curl -L -O https://github.com/Yossi/omer/archive/pythonanywhere.zip
echo Unzipping...
unzip pythonanywhere.zip
unzip -z pythonanywhere.zip | sed -n 2p > omer-pythonanywhere/version.hash
rm pythonanywhere.zip
echo Deleted pythonanywhere.zip
rm -rf omer
mv omer-pythonanywhere omer
echo Updated omer/
mv omer/deploy.sh deploy.sh
echo Updated deploy.sh
cd omer
source virtualenvwrapper.sh
workon omer
echo Virtualenv omer activated

echo Install requirements one by one in order to not blow up storage

while read -r line || [[ -n "$line" ]]; do
    if [[ $line != \#* ]]; then
        pip install -U --upgrade-strategy only-if-needed "$line"
    fi
done < requirements.txt

# pip install -U --upgrade-strategy only-if-needed -r requirements.txt
echo Attempting to list outdated packages:
pip list --outdated
rm -rf ../.cache
rm -rf .github/
rm .gitignore
rm requirements.txt
echo Done. Now go reload site from the Web tab.
