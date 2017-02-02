# ML-Infra

## Config

### Install Python3
```
wget https://www.python.org/ftp/python/3.4.2/Python-3.4.2.tgz
tar zxvf Python-3.4.2.tgz
cd Python-3.4.2
sudo yum install gcc
./configure --prefix=/opt/python3
make
sudo make install
sudo ln -s /opt/python3/bin/python3 /usr/bin/python3
sudo ln -s /opt/python3/bin/easy_install-3.4 /usr/bin/easy_install3
sudo ln -s /opt/python3/bin/pip3 /usr/bin/pip3.4
sudo ln -s /opt/python3/bin/pydoc3 /usr/bin/pydoc3
sudo ln -s /opt/python3/bin/pyenv /usr/bin/pyenv
```
### Setup VirtualEnv
```
virtualenv ~/ML-Infa-env
source ~/ML-Infa-env/bin/activate
```

### Install Git
`sudo yum install git`

### Launch Project

`git clone git@github.com:emilemathieu/ML-Infra.git`
