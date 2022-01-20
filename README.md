# Projeto exemplo utilizando Django + Celery + RabbitMQ + Selenium
Projeto de inclusão de movimentações de compra/venda de ações na bolsa de valores, utilizando o framework Django, Celery para rotina diária de obter as \
cotações do dia anterior via cron do Celery utilizando o Selenium para buscar e atualizar os valores na base de dados


### Clonando projeto
git clone https://github.com/AyrtonMoises/django_bolsa.git

### Criando ambiente
python3 -m venv venv

### Ativando ambiente virtual Linux
source venv/bin/activate

### Instalando pacotes
pip install -r requirements.txt

### Realiza as migrações
python manage.py migrate

### Cria superusuario ao admin
python manage.py createsuperuser

### Inicia servidor
python manage.py runserver

### Instalando o RabbitMQ Ubuntu (Pode ser outro worker de preferência)
sudo apt-get install rabbitmq-server\
sudo systemctl enable rabbitmq-server\
sudo systemctl start rabbitmq-server\
sudo systemctl status rabbitmq-server

### Iniciando Celery com worker e beat (somente para fins de desenvolvimento estarão juntos no mesmo comando)
#### Abra outro terminal e ative o mesmo ambiente virtual do projeto
celery -A setup worker -l INFO -Q fila_padrao -B --scheduler django_celery_beat.schedulers:DatabaseScheduler


### Acessando pelo browser
http://localhost:8000/dashboard/


### Acesse o admin para acompanhar as tasks e controlar as tasks de crontab
http://localhost:8000/admin/
