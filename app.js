// Firebase configuration (adicione as suas credenciais do Firebase aqui)
const firebaseConfig = {
    apiKey: "SUA_API_KEY",
    authDomain: "SEU_DOMINIO.firebaseapp.com",
    projectId: "SEU_ID_PROJETO",
    storageBucket: "SEU_BUCKET.firebaseapp.com",
    messagingSenderId: "SEU_MESSAGING_ID",
    appId: "SEU_APP_ID",
};

// Inicializando Firebase
const app = firebase.initializeApp(firebaseConfig);
const db = firebase.firestore();

// Função para adicionar diária (meio período por padrão)
function adicionarDiaria() {
    const diaria = prompt("Você trabalhou o dia todo? (sim/não)");
    const valor = diaria.toLowerCase() === 'sim' ? 90 : 45;
    const hoje = new Date().toLocaleDateString();

    db.collection('diarias').add({
        data: hoje,
        valor: valor
    }).then(() => {
        document.getElementById('result').innerText = 'Diária adicionada com sucesso!';
    }).catch((error) => {
        console.error("Erro ao adicionar diária: ", error);
    });
}

// Função para remover a última diária inserida
function removerDiaria() {
    db.collection('diarias').orderBy('data', 'desc').limit(1).get().then((snapshot) => {
        snapshot.forEach((doc) => {
            db.collection('diarias').doc(doc.id).delete().then(() => {
                document.getElementById('result').innerText = 'Última diária removida com sucesso!';
            }).catch((error) => {
                console.error("Erro ao remover diária: ", error);
            });
        });
    });
}

// Função para mostrar o total de diárias adicionadas
function mostrarTotalDiarias() {
    db.collection('diarias').get().then((snapshot) => {
        const totalDiarias = snapshot.size;
        document.getElementById('result').innerText = `Total de diárias: ${totalDiarias}`;
    }).catch((error) => {
        console.error("Erro ao buscar diárias: ", error);
    });
}

// Função para mostrar o saldo total (somando os valores das diárias)
function mostrarSaldoTotal() {
    db.collection('diarias').get().then((snapshot) => {
        let saldoTotal = 0;
        snapshot.forEach((doc) => {
            saldoTotal += doc.data().valor;
        });
        document.getElementById('result').innerText = `Saldo total: R$${saldoTotal}`;
    }).catch((error) => {
        console.error("Erro ao calcular saldo: ", error);
    });
}
