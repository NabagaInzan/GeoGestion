// Gestionnaire d'erreur global pour les requêtes AJAX
$(document).ajaxError(function(event, jqXHR, settings, error) {
    if (jqXHR.status === 401) {
        window.location.href = '/';
    }
});

$(document).ready(function() {
    let employeesTable;
    let currentEmployeeId = null;

    // Fonction pour formater le nom
    function formatName(name) {
        if (!name) return '';
        return name.toUpperCase();
    }

    // Fonction pour formater le prénom
    function formatFirstName(name) {
        if (!name) return '';
        return name.charAt(0).toUpperCase() + name.slice(1).toLowerCase();
    }

    // Fonction pour réinitialiser les statistiques
    function resetStats() {
        $('.total-employees').text('--');
        $('.gender-stats').text('--/--');
        $('.contract-stats').text('--');
        $('.availability-stats').text('--');
    }

    // Fonction pour charger les statistiques
    function loadStats() {
        $('.stats-loader').show();
        $.ajax({
            url: '/api/stats',
            method: 'GET',
            success: function(response) {
                if (response.success && response.stats) {
                    const stats = response.stats;
                    
                    // Mise à jour du total des employés
                    $('.total-employees').text(stats.total_employees || 0);
                    
                    // Mise à jour de la répartition homme/femme
                    let mCount = stats.gender_distribution?.M || 0;
                    let fCount = stats.gender_distribution?.F || 0;
                    $('.gender-stats').text(`${mCount}/${fCount}`);
                    
                    // Mise à jour des contrats actifs
                    $('.contract-stats').text(stats.contract_distribution?.active || 0);
                    
                    // Mise à jour de la disponibilité
                    let siegeCount = stats.availability_distribution?.siege || 0;
                    let interieurCount = stats.availability_distribution?.interieur || 0;
                    $('.availability-stats').text(`${siegeCount}/${interieurCount}`);
                    
                    showToast('Statistiques mises à jour', 'fas fa-chart-bar');
                } else {
                    console.error('Format de réponse invalide:', response);
                    showToast('Erreur lors de la mise à jour des statistiques', 'fas fa-exclamation-triangle');
                    resetStats();
                }
            },
            error: function(xhr, status, error) {
                console.error('Erreur lors du chargement des statistiques:', error);
                showToast('Erreur de connexion', 'fas fa-exclamation-triangle');
                resetStats();
            },
            complete: function() {
                $('.stats-loader').hide();
            }
        });
    }

    // Configuration de DataTables
    employeesTable = $('#employeesTable').DataTable({
        ajax: {
            url: '/api/employees',
            dataSrc: ''
        },
        columns: [
            { 
                data: 'last_name',
                render: function(data, type, row) {
                    return formatName(data);
                }
            },
            { 
                data: 'first_name',
                render: function(data, type, row) {
                    return formatFirstName(data);
                }
            },
            { data: 'position' },
            { data: 'contact' },
            { data: 'gender' },
            { 
                data: 'availability',
                render: function(data, type, row) {
                    if (data === 'Au siège') {
                        return '<span class="badge bg-success">Au siège</span>';
                    } else if (data === 'À l\'intérieur') {
                        return '<span class="badge bg-warning">À l\'intérieur</span>';
                    }
                    return data;
                }
            },
            {
                data: null,
                render: function(data, type, row) {
                    return `
                        <div class="btn-group" role="group">
                            <button type="button" class="btn btn-sm btn-primary edit-btn" data-id="${row.id}">
                                <i class="fas fa-edit"></i>
                            </button>
                            <button type="button" class="btn btn-sm btn-danger delete-btn" data-id="${row.id}">
                                <i class="fas fa-trash"></i>
                            </button>
                        </div>
                    `;
                }
            }
        ],
        order: [[0, 'asc']],
        language: {
            url: 'https://cdn.datatables.net/plug-ins/1.13.6/i18n/fr-FR.json'
        }
    });

    // Gestionnaire pour le formulaire d'ajout/modification
    $('#addEmployeeForm').on('submit', function(e) {
        e.preventDefault();
        
        // Récupérer les données du formulaire
        const formData = new FormData(this);
        const data = {};
        formData.forEach((value, key) => {
            data[key] = value;
        });
        
        // Ajouter l'ID de l'opérateur depuis la session
        $.ajax({
            url: '/api/employees' + (currentEmployeeId ? `/${currentEmployeeId}` : ''),
            method: currentEmployeeId ? 'PUT' : 'POST',
            contentType: 'application/json',
            data: JSON.stringify(data),
            success: function(response) {
                if (response.success) {
                    $('#addEmployeeModal').modal('hide');
                    employeesTable.ajax.reload();
                    loadStats();
                    showToast(
                        currentEmployeeId ? 'Employé modifié avec succès' : 'Employé ajouté avec succès',
                        'fas fa-check-circle'
                    );
                    $('#addEmployeeForm')[0].reset();
                } else {
                    showToast('Erreur: ' + (response.error || 'Une erreur est survenue'), 'fas fa-times-circle');
                }
            },
            error: function(xhr) {
                console.error('Erreur:', xhr.responseJSON);
                showToast('Erreur: ' + (xhr.responseJSON?.error || 'Une erreur est survenue'), 'fas fa-times-circle');
            }
        });
    });

    // Réinitialisation du formulaire lors de la fermeture du modal
    $('#addEmployeeModal').on('hidden.bs.modal', function() {
        $('#addEmployeeForm')[0].reset();
        currentEmployeeId = null;
        $('.modal-title').html('<i class="fas fa-user-plus me-2"></i>Ajouter un Employé');
    });

    // Initialisation
    loadStats();
    setInterval(loadStats, 60000);
});
