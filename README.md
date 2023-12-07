# Escopo geral

## Instalar/Ativar ambiente virtual Python
O objetivo deste é apenas separar o ambiente do projeto do ambiente principal. Não é obrigatório caso já esteja acostumado em rodar direto o python e suas versões na no ambiente principal do sistema operacional.

### Benefícios
- Isolamento de ambientes, evitando conflitos entre versões de bibliotecas.
- Facilitação do controle de dependências e versões do Python.
- Maior portabilidade dos projetos entre diferentes ambientes de desenvolvimento.

### Quick Start
Há possibilidade de estar instalado o necessário para rodar ambiente virtual. Caso seja o caso inicie por criar o ambiente.
```bash
python3 -m venv .env
```
E para ativar.
```bash
source <absolute path> .env/bin/activate
```
Após ativado pode rodar o comando para instalar todas as dependencies necessárias para o projeto, assim não afetando no ambiente global:
```bash
pip install -r requirements.txt
```

- ⚠️ **Alerta:**
  O ambiente virtual está sendo recomendo por não ter implementado em docker o projeto por enquanto.

## Caso Precise instalar Virtual env pode seguir os próximos passos

### 1. Instalação do Virtualenv
O primeiro passo é instalar a ferramenta `virtualenv`, que permite a criação de ambientes virtuais.

```bash
pip install virtualenv
```

### 2. Criar um Ambiente Virtual
Na raiz do seu projeto, crie um ambiente virtual usando o seguinte comando:

```bash
virtualenv venv
```

Isso criará um diretório chamado `venv` que conterá o ambiente virtual.

### 3. Ativar o Ambiente Virtual
Para ativar o ambiente virtual, utilize o comando apropriado conforme o sistema operacional:
- No MacOS/Linux:

    ```bash
    source venv/bin/activate
    ```

Após a ativação, o prompt de comando deve indicar o nome do ambiente virtual.

### 4. Instalar Dependências
Com o ambiente virtual ativado, use o comando `pip` para instalar as dependências do seu projeto. Isso garantirá que as bibliotecas sejam instaladas no ambiente virtual, não afetando o ambiente global.

```bash
pip install -r requirements.txt
```

### 5. Desativar o Ambiente Virtual
Quando terminar de trabalhar no projeto, desative o ambiente virtual:

```bash
deactivate
```

### Dica Adicional: Gerar um requirements.txt
Para gerar um arquivo `requirements.txt` que lista todas as dependências do seu projeto, execute o seguinte comando no ambiente virtual:

```bash
pip freeze > requirements.txt
```

# Crawl
As informações especificas para rodar e utilizar o crawl estão no arquivo [README.md](/crawl/) do diretório crawl.
