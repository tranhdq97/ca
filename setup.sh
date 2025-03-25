# System upgrade
sudo apt update && sudo apt upgrade -y
sudo apt-get install libmysqlclient-dev

# Docker installation
sudo apt install -y ca-certificates curl gnupg
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo tee /etc/apt/keyrings/docker.asc > /dev/null
sudo chmod a+r /etc/apt/keyrings/docker.asc
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
sudo docker --version
sudo systemctl status docker
sudo usermod -aG docker $USER
newgrp docker

# Setup mysql by docker
docker pull mysql:latest
docker run --name mysql-container -e MYSQL_ROOT_PASSWORD=1345 -d -p 3306:3306 --restart=unless-stopped mysql:latest
docker exec -it mysql mysql -u root -p # Enter password: 1345 and run the following command: CREATE SCHEMA ca_db;

# Setup python environment
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Setup project
cp .env.example .env
flask db init
flask db migrate
flask db upgrade
