document.addEventListener('DOMContentLoaded', function() {
    const loginForm = document.getElementById('loginForm');
    const usernameSelect = document.getElementById('username');
    const contactInput = document.getElementById('contact');
    const passwordInput = document.getElementById('password');
    const adminSwitch = document.getElementById('adminSwitch');
    const passwordToggle = document.querySelector('.password-toggle');

    // Charger la liste des acteurs
    fetch('/get_operators')
        .then(response => response.json())
        .then(operators => {
            operators.forEach(operator => {
                const option = document.createElement('option');
                option.value = operator.id;
                option.textContent = operator.name;
                option.dataset.contact = operator.contact1;
                usernameSelect.appendChild(option);
            });
        })
        .catch(error => console.error('Erreur lors du chargement des acteurs:', error));

    // Gérer le changement d'acteur
    usernameSelect.addEventListener('change', function() {
        const selectedOption = this.options[this.selectedIndex];
        if (selectedOption && !adminSwitch.checked) {
            contactInput.value = selectedOption.dataset.contact || '';
        }
    });

    // Gérer le switch admin
    adminSwitch.addEventListener('change', function() {
        contactInput.readOnly = !this.checked;
        if (!this.checked) {
            const selectedOption = usernameSelect.options[usernameSelect.selectedIndex];
            contactInput.value = selectedOption.dataset.contact || '';
        } else {
            contactInput.value = '';
            contactInput.focus();
        }
    });

    // Gérer l'affichage/masquage du mot de passe
    passwordToggle.addEventListener('click', function() {
        const type = passwordInput.type === 'password' ? 'text' : 'password';
        passwordInput.type = type;
        this.querySelector('i').classList.toggle('fa-eye');
        this.querySelector('i').classList.toggle('fa-eye-slash');
    });

    // Gérer la soumission du formulaire
    loginForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const formData = {
            operator_id: usernameSelect.value,
            contact: contactInput.value,
            password: passwordInput.value,
            is_admin: adminSwitch.checked
        };

        fetch('/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(formData)
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                window.location.href = data.redirect;
            } else {
                // Afficher l'erreur
                const alert = document.createElement('div');
                alert.className = 'alert alert-danger';
                alert.textContent = data.error;
                loginForm.insertBefore(alert, loginForm.firstChild);
                
                // Supprimer l'alerte après 3 secondes
                setTimeout(() => alert.remove(), 3000);
            }
        })
        .catch(error => {
            console.error('Erreur:', error);
            const alert = document.createElement('div');
            alert.className = 'alert alert-danger';
            alert.textContent = 'Une erreur est survenue. Veuillez réessayer.';
            loginForm.insertBefore(alert, loginForm.firstChild);
            setTimeout(() => alert.remove(), 3000);
        });
    });
});
