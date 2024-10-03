document.addEventListener("DOMContentLoaded", function() {
    // Calcular o valor acumulado ao carregar a página
    fetch('/calculate_total')
        .then(response => response.json())
        .then(data => {
            document.getElementById('total-value').textContent = data.total;
        });

    // Formulário de cancelamento de dia
    const cancelForm = document.getElementById('cancel-form');
    cancelForm.addEventListener('submit', function(event) {
        event.preventDefault();

        const formData = new FormData(cancelForm);
        const date = formData.get('date');
        const reason = formData.get('reason');

        fetch('/cancel_day', {
            method: 'POST',
            body: new URLSearchParams(formData)
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert('Dia cancelado com sucesso!');
                location.reload();
            }
        });
    });
});
