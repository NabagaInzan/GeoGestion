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
        $('#totalEmployees').text('--');
        $('#availableEmployees').html('--');
        $('#maleEmployees').text('--');
        $('#femaleEmployees').text('--');
    }

    // Fonction pour charger les statistiques
    function loadStats() {
        $.ajax({
            url: '/api/stats',
            method: 'GET',
            success: function(response) {
                if (response.success) {
                    const stats = response.stats;
                    $('#totalEmployees').text(stats.total || 0);
                    $('#availableEmployees').html(`
                        Au siège: ${stats.siege || 0}<br>
                        À l'intérieur: ${stats.interieur || 0}
                    `);
                    $('#maleEmployees').text(stats.male || 0);
                    $('#femaleEmployees').text(stats.female || 0);
                }
            },
            error: function(xhr) {
                console.error('Erreur lors du chargement des statistiques:', xhr);
            }
        });
    }

    // Initialisation de la table avec DataTables
    employeesTable = $('#employeesTable').DataTable({
        ajax: {
            url: '/api/employees',
            dataSrc: ''
        },
        columns: [
            { data: 'last_name' },
            { data: 'first_name' },
            { data: 'position' },
            { data: 'gender' },
            { 
                data: 'availability',
                render: function(data) {
                    const badgeClass = data === 'Au siège' ? 'bg-success' : 'bg-primary';
                    return `<span class="badge ${badgeClass}">${data}</span>`;
                }
            },
            {
                data: null,
                render: function(data, type, row) {
                    return `
                        <button class="btn btn-sm btn-primary edit-btn" data-id="${row.id}">
                            <i class="fas fa-edit"></i>
                        </button>
                        <button class="btn btn-sm btn-danger delete-btn" data-id="${row.id}">
                            <i class="fas fa-trash"></i>
                        </button>
                    `;
                }
            }
        ],
        dom: 'Bfrtip',
        buttons: [
            {
                extend: 'excel',
                text: '<i class="fas fa-file-excel"></i> Excel',
                className: 'btn btn-success',
                exportOptions: {
                    columns: [0, 1, 2, 3, 4]
                }
            },
            {
                extend: 'pdf',
                text: '<i class="fas fa-file-pdf"></i> PDF',
                className: 'btn btn-danger',
                exportOptions: {
                    columns: [0, 1, 2, 3, 4]
                }
            },
            {
                extend: 'print',
                text: '<i class="fas fa-print"></i> Imprimer',
                className: 'btn btn-info',
                exportOptions: {
                    columns: [0, 1, 2, 3, 4]
                }
            }
        ],
        language: {
            url: '//cdn.datatables.net/plug-ins/1.13.4/i18n/fr-FR.json'
        }
    });

    // Gestionnaire pour le bouton de modification
    $('#employeesTable').on('click', '.edit-btn', function() {
        const employeeId = $(this).data('id');
        
        // Afficher le loader
        $('.loader').show();
        
        // Récupérer les données de l'employé
        $.ajax({
            url: `/api/employees/${employeeId}`,
            method: 'GET',
            success: function(response) {
                if (response && response.id) {
                    // Remplir le formulaire avec les données
                    $('#lastName').val(response.last_name || '');
                    $('#firstName').val(response.first_name || '');
                    $('#position').val(response.position || '');
                    $('#contact').val(response.contact || '');
                    $('#gender').val(response.gender || '');
                    $('#contractDuration').val(response.contract_duration || '');
                    $('#birthDate').val(response.birth_date || '');
                    $('#availability').val(response.availability || '');
                    $('#additionalInfo').val(response.additional_info || '');
                    
                    // Stocker l'ID de l'employé en cours d'édition
                    currentEmployeeId = employeeId;
                    
                    // Mettre à jour le titre du modal
                    $('.modal-title').html('<i class="fas fa-user-edit me-2"></i>Modifier un Employé');
                    
                    // Afficher le modal
                    $('#addEmployeeModal').modal('show');
                } else {
                    showToast('Erreur : Données de l\'employé non trouvées', 'fas fa-times-circle');
                }
            },
            error: function(xhr) {
                showToast('Erreur : ' + (xhr.responseJSON?.error || 'Erreur de chargement'), 'fas fa-times-circle');
            },
            complete: function() {
                $('.loader').hide();
            }
        });
    });

    // Gestionnaire pour le bouton de suppression
    $('#employeesTable').on('click', '.delete-btn', function() {
        const employeeId = $(this).data('id');
        
        if (confirm('Êtes-vous sûr de vouloir supprimer cet employé ?')) {
            // Afficher le loader
            $('.loader').show();
            
            // Envoyer la requête de suppression
            $.ajax({
                url: `/api/employees/${employeeId}`,
                method: 'DELETE',
                success: function(response) {
                    if (response.success) {
                        employeesTable.ajax.reload();
                        loadStats();
                        showToast('Employé supprimé avec succès', 'fas fa-check-circle');
                    } else {
                        showToast('Erreur : ' + (response.error || 'Erreur de suppression'), 'fas fa-times-circle');
                    }
                },
                error: function(xhr) {
                    showToast('Erreur : ' + (xhr.responseJSON?.error || 'Erreur de suppression'), 'fas fa-times-circle');
                },
                complete: function() {
                    $('.loader').hide();
                }
            });
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
        
        // Afficher le loader
        $('.loader').show();
        
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
                    currentEmployeeId = null;
                } else {
                    showToast('Erreur: ' + (response.error || 'Une erreur est survenue'), 'fas fa-times-circle');
                }
            },
            error: function(xhr) {
                console.error('Erreur:', xhr.responseJSON);
                showToast('Erreur: ' + (xhr.responseJSON?.error || 'Une erreur est survenue'), 'fas fa-times-circle');
            },
            complete: function() {
                $('.loader').hide();
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
