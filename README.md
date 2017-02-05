# ML-Infra

## Config
```
sudo apt-get update
sudo apt-get install -y python3-pip python3-venv nginx nodejs npm nodejs-legacy
sudo npm install -g pm2

mkdir environments
cd environments

pyvenv --without-pip venv
source venv/bin/activate
curl https://bootstrap.pypa.io/get-pip.py | python
deactivate
source venv/bin/activate

git clone https://github.com/emilemathieu/ML-Infra.git
cd ML-Infra/app
pip install -r requirements.txt
```


## Development

Add the project address to your hosts:
```shell
sudo /bin/bash -c 'echo "10.0.0.10  ml-infra.dev" >> /private/etc/hosts'
```
You must have the lastest version of [Vagrant](https://www.vagrantup.com/) installed.

**To run a Vagrant command, you have to go the provisioning folder where the Vagranfile is situated:**
```
cd devops/provisioning
```

Install roles:
```
ansible-galaxy install -r requirements.txt --force
```

Then start and provision a **virtual machine**:
```
vagrant up
```

The NodeJs server is located under `/home//back/current`.
To start the server, you can thus run:
```
vagrant ssh
source ../venvs/myenv/bin/activate
cd /home/ML-Infra/current
python main.py
```

Now, you should be able to see a Hello World when navigating to [http://ml-infra.dev](http://ml-infra.dev).


## Production

The **Production** environment is hosted on AWS.

Add the project address to your hosts:
```shell
sudo /bin/bash -c 'echo "34.250.87.12  ml-infra.prod" >> /private/etc/hosts'
```

### Access
```
ssh-add AWS_KEY.pem
ssh ubuntu@ml-infra.prod
```

### Provisioning

First, go to the provisioning folder:
```
cd devops/provisioning
```

Install roles:
```
ansible-galaxy install -r requirements.txt --force
```

Run playbook:
```
ansible-playbook playbook.yml -i inventory/production -vvvv
```

### Deploy

### Launch
``
pm2 startOrRestart main.py
```
