# **Documentação**

### Dependências

> Python 3.x; Node 12.x; Django 3.x; Bootstrap 4

### Instruções de uso

1. Abra o terminal e, na pasta do projeto, digite o comando

    ```JavaScript
        python3 manage.py runserver
    ```
    Para executar o projeto.

2. Após alterações na base de dados do Django, executar migração com os seguintes comandos

    ```JavaScript
        python3 manage.py makemigrations
        python3 manage.py migrate
    ```

### Desenvolvimento

> Cada membro do time deverá trabalhar em sua branch e, após o término do desenvolvimento de cada etapa(feature), deverá efetuar commit para a master.

     Tipos de branch
        1. Feature/nome_da_feature
        2. Backend/nome_do_serviço
        3. Bugfix/bug_a_ser_corrigido
        4. Frontend/nome_do_componente_ou_elemento