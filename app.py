import json
import base64
import requests
from flask import Flask, render_template, request, redirect

app = Flask(__name__)

# Configurações do GitHub
GITHUB_REPO = 'JOAO11092005/trabalho'  # Substitua pelo seu repositório
GITHUB_TOKEN = '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'  # Substitua pelo seu token do GitHub
FILE_PATH = 'trabalho.json'

def fetch_data():
    """Busca o JSON do repositório no GitHub ou cria um novo se não existir."""
    url = f'https://api.github.com/repos/{GITHUB_REPO}/contents/{FILE_PATH}'
    response = requests.get(url, headers={'Authorization': f'token {GITHUB_TOKEN}'})
    
    if response.status_code == 200:
        content = response.json()
        json_data = json.loads(requests.get(content['download_url']).text)
        return json_data
    elif response.status_code == 404:
        # Se o arquivo não existe, cria um novo com um objeto JSON vazio
        initial_data = {}
        create_github_file(initial_data)
        return initial_data
    else:
        print(f"Erro ao buscar dados: {response.status_code}, {response.text}")
        return {}

def create_github_file(data):
    """Cria o arquivo JSON no GitHub."""
    url = f'https://api.github.com/repos/{GITHUB_REPO}/contents/{FILE_PATH}'
    message = "Criando trabalho.json"
    new_file_content = json.dumps(data)

    # Codifica o conteúdo em Base64
    encoded_content = base64.b64encode(new_file_content.encode('utf-8')).decode('utf-8')

    # Enviando a criação do arquivo
    response = requests.put(url, headers={'Authorization': f'token {GITHUB_TOKEN}'}, json={
        "message": message,
        "content": encoded_content,
    })
    
    if response.status_code == 201:
        print("Arquivo criado com sucesso.")
    else:
        print(f"Erro ao criar arquivo: {response.status_code}, {response.text}")

def update_github(data):
    """Atualiza o arquivo JSON no GitHub."""
    url = f'https://api.github.com/repos/{GITHUB_REPO}/contents/{FILE_PATH}'
    response = requests.get(url, headers={'Authorization': f'token {GITHUB_TOKEN}'})
    
    if response.status_code == 200:
        content = response.json()
        sha = content['sha']
        message = "Atualizando trabalho.json"
        new_file_content = json.dumps(data)

        # Codifica o conteúdo em Base64
        encoded_content = base64.b64encode(new_file_content.encode('utf-8')).decode('utf-8')

        # Enviando a atualização
        update_response = requests.put(url, headers={'Authorization': f'token {GITHUB_TOKEN}'}, json={
            "message": message,
            "content": encoded_content,
            "sha": sha
        })
        
        if update_response.status_code == 200:
            print("Arquivo atualizado com sucesso.")
            return True
        else:
            print(f"Erro ao atualizar o arquivo: {update_response.status_code}, {update_response.text}")
            return False

    elif response.status_code == 404:
        # Se o arquivo não existe, cria um novo
        create_github_file(data)
        return True  # Retorna True pois o arquivo foi criado com sucesso
    else:
        print(f"Erro ao buscar o arquivo para atualização: {response.status_code}, {response.text}")
        return False

@app.route('/')
def index():
    data = fetch_data()
    total_receber = sum(details['valor_diaria'] for details in data.values())
    total_diarias = len(data)
    return render_template('index.html', data=data, total_receber=total_receber, total_diarias=total_diarias)

@app.route('/add_day', methods=['POST'])
def add_day():
    date = request.form['date']
    valor_diaria = float(request.form['valor_diaria'])
    meio_periodo = request.form['meio_periodo'] == 'true'
    diaria_paga = request.form.get('diaria_paga', 'false') == 'true'  # Novo campo para diária paga

    data = fetch_data()
    data[date] = {
        'status': 'Pendente',
        'valor_diaria': valor_diaria,
        'meio_periodo': meio_periodo,
        'diaria_paga': diaria_paga  # Adiciona o campo de diária paga
    }
    
    if update_github(data):
        return redirect('/')
    return "Erro ao atualizar o GitHub", 500

@app.route('/remove_day', methods=['POST'])
def remove_day():
    date = request.form['date']
    
    data = fetch_data()
    if date in data:
        del data[date]
    
    if update_github(data):
        return redirect('/')
    return "Erro ao atualizar o GitHub", 500

@app.route('/cancel_day', methods=['POST'])
def cancel_day():
    date = request.form['date']
    motivo = request.form['motivo']
    indisponibilidade = int(request.form['indisponibilidade'])

    data = fetch_data()
    if date in data:
        data[date]['status'] = f'Cancelado: {motivo}, Indisponível por {indisponibilidade} dias'
    
    if update_github(data):
        return redirect('/')
    return "Erro ao atualizar o GitHub", 500

@app.route('/mark_full_day', methods=['POST'])
def mark_full_day():
    date = request.form['date']
    full_day = request.form['full_day'] == 'true'

    data = fetch_data()
    if date in data:
        data[date]['meio_periodo'] = not full_day
        data[date]['valor_diaria'] = 90.0 if not full_day else 45.0  # Ajuste o valor conforme necessário

    if update_github(data):
        return redirect('/')
    return "Erro ao atualizar o GitHub", 500

@app.route('/mark_paid', methods=['POST'])
def mark_paid():
    date = request.form['date']
    
    data = fetch_data()
    if date in data:
        data[date]['diaria_paga'] = True  # Marca a diária como paga

    if update_github(data):
        return redirect('/')
    return "Erro ao atualizar o GitHub", 500

if __name__ == '__main__':
    app.run(debug=True)
