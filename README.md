# **Documentação**

### Dependências

> Python 3.x; Node 12.x; Django 3.x; Vue 2.x

### Instruções de uso

1. Abra o terminal e, na pasta do projeto, digite o comando como administrador ou superuser
    
    ```cmd
        pip3 install -r requirements.txt
    ```
    OBS: https://stackoverflow.com/questions/13200330/how-to-install-python-levenshtein-on-windows

2. Digite o comando

    ```JavaScript
        python3 manage.py runserver
    ```
    Para executar o projeto.

3. Após alterações na base de dados do Django, executar migração com os seguintes comandos

    ```JavaScript
        python3 manage.py makemigrations
        python3 manage.py migrate
    ```

### Desenvolvimento

> Cada membro do time deverá trabalhar em sua branch e, após o término do desenvolvimento de cada etapa(feature), deverá efetuar commit para a master

     Tipos de branch
        1. Feature/nome_da_feature
        2. Backend/nome_do_serviço
        3. Bugfix/bug_a_ser_corrigido
        4. Frontend/nome_do_componente_ou_elemento

### Notas de Documentação

* A rota front-end começa no `.\App\templates\index.html`
* O ideal é que documentemos cada elemento que não seja "óbvio" conhecer o mesmo
* Outro ideal é documentar a "rota" que o programa segue, a fim de educar outros que não possuem o mesmo grau de conhecimento, como no primeiro bullet point desse parágrafo, por exemplo