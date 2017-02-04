# ML-Infra

## Config
```
sudo apt-get update
sudo apt-get install python3-pip
sudo apt-get install -y python3-venv

mkdir environments
cd environments

pyvenv --without-pip venvdir
source venvdir/bin/activate
curl https://bootstrap.pypa.io/get-pip.py | python
deactivate
source venvdir/bin/activate

git clone https://github.com/emilemathieu/ML-Infra.git
cd ML-Infra/app
pip install -r requirements.txt
```

```
sudo apt-get install nginx nodejs npm
pip install gunicorn
npm install pm2
```