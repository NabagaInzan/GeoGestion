// Gestionnaire d'erreur global pour les requêtes AJAX
$(document).ajaxError(function(event, jqXHR, settings, error) {
    if (jqXHR.status === 401) {
        window.location.href = '/';
    }
});

// Variable globale pour la table
let employeesTable;

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
    // Afficher les loaders
    $('.stats-loader').show();
    $('.stats-value').text('--');
    
    $.ajax({
        url: '/api/stats',
        method: 'GET',
        success: function(response) {
            if (response.success) {
                const stats = response.stats;
                
                // Mise à jour des statistiques
                $('#totalEmployees').text(stats.total);
                
                // Mise à jour de la situation géographique
                const availableHtml = `
                    <div class="d-flex flex-column">
                        <span class="badge badge-siege mb-1" style="color: black;">Au siège: ${stats.siege}</span>
                        <span class="badge badge-interieur" style="color: black;">À l'intérieur: ${stats.interieur}</span>
                    </div>
                `;
                $('#availableEmployees').html(availableHtml);
                
                // Mise à jour du nombre d'hommes et de femmes
                $('#maleEmployees').text(stats.male);
                $('#femaleEmployees').text(stats.female);
                
                // Animation des compteurs
                $('.counter-value').each(function () {
                    $(this).prop('Counter', 0).animate({
                        Counter: $(this).text()
                    }, {
                        duration: 1000,
                        easing: 'swing',
                        step: function (now) {
                            $(this).text(Math.ceil(now));
                        }
                    });
                });
            } else {
                showToast('Erreur: ' + (response.error || 'Erreur de chargement des statistiques'), 'fas fa-times-circle');
            }
        },
        error: function(xhr) {
            console.error('Erreur lors du chargement des statistiques:', xhr);
            showToast('Erreur de connexion', 'fas fa-times-circle');
        },
        complete: function() {
            $('.stats-loader').hide();
        }
    });
}

// Fonction pour initialiser la table
function initializeEmployeesTable() {
    employeesTable = $('#employeesTable').DataTable({
        ajax: {
            url: '/api/employees',
            dataSrc: ''
        },
        columns: [
            { data: 'last_name' },
            { data: 'first_name' },
            { data: 'position' },
            { data: 'contact' },
            { 
                data: 'gender',
                render: function(data) {
                    return data === 'M' ? 'Homme' : 'Femme';
                }
            },
            { 
                data: 'availability',
                render: function(data) {
                    const badgeClass = data === 'Au siège' ? 'badge-siege' : 'badge-interieur';
                    return `<span class="badge ${badgeClass}" style="color: black;">${data}</span>`;
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
        order: [[0, 'asc']],
        dom: 'Bfrtip',
        buttons: [
            {
                extend: 'excel',
                text: '<i class="fas fa-file-excel"></i> Excel',
                className: 'btn btn-success',
                exportOptions: {
                    columns: [0, 1, 2, 3, 4, 5]
                }
            },
            {
                extend: 'pdf',
                text: '<i class="fas fa-file-pdf"></i> PDF',
                className: 'btn btn-danger',
                exportOptions: {
                    columns: [0, 1, 2, 3, 4, 5]
                }
            },
            {
                extend: 'print',
                text: '<i class="fas fa-print"></i> Imprimer',
                className: 'btn btn-info',
                exportOptions: {
                    columns: [0, 1, 2, 3, 4, 5]
                }
            }
        ],
        language: {
            url: '//cdn.datatables.net/plug-ins/1.13.4/i18n/fr-FR.json'
        }
    });
}

// Fonction pour calculer l'âge
function calculateAge(birthdate) {
    const today = new Date();
    const birth = new Date(birthdate);
    let age = today.getFullYear() - birth.getFullYear();
    const monthDiff = today.getMonth() - birth.getMonth();
    
    if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birth.getDate())) {
        age--;
    }
    return age;
}

// Fonction pour calculer la durée du contrat
function calculateContractDuration(startDate, endDate) {
    const start = new Date(startDate);
    const end = new Date(endDate);
    const diffTime = Math.abs(end - start);
    const diffYears = diffTime / (1000 * 60 * 60 * 24 * 365.25);
    const years = Math.floor(diffYears);
    const months = Math.floor((diffYears - years) * 12);
    
    return {
        years: years,
        months: months
    };
}

// Fonction pour convertir les mois en années et mois
function convertMonthsToYearsAndMonths(totalMonths) {
    const years = Math.floor(totalMonths / 12);
    const months = totalMonths % 12;
    let durationText = '';
    
    if (years > 0) {
        durationText += `${years} an${years > 1 ? 's' : ''}`;
    }
    if (months > 0) {
        if (durationText) durationText += ' et ';
        durationText += `${months} mois`;
    }
    if (!durationText) {
        durationText = `${totalMonths} mois`;
    }
    return durationText;
}

// Initialisation au chargement de la page
$(document).ready(function() {
    let currentEmployeeId = null;

    initializeEmployeesTable();
    loadStats();
    
    // Actualisation automatique des statistiques
    setInterval(loadStats, 30000);

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

    // Gestionnaires d'événements pour les dates
    $('#birthdate').on('change', function() {
        const age = calculateAge(this.value);
        $('#age-display').text(`Âge: ${age} ans`);
    });

    $('#contract_start, #contract_end').on('change', function() {
        const startDate = $('#contract_start').val();
        const endDate = $('#contract_end').val();
        
        if (startDate && endDate) {
            const duration = calculateContractDuration(startDate, endDate);
            let durationText = '';
            
            if (duration.years > 0) {
                durationText += `${duration.years} an${duration.years > 1 ? 's' : ''}`;
            }
            if (duration.months > 0) {
                if (durationText) durationText += ' et ';
                durationText += `${duration.months} mois`;
            }
            
            $('#contract-duration-display').text(`Durée: ${durationText}`);
        }
    });

    // Gestionnaire d'événements pour la durée du contrat
    $('#contract_duration').on('input', function() {
        const months = parseInt(this.value) || 0;
        if (months > 0) {
            const durationText = convertMonthsToYearsAndMonths(months);
            $('#contract-duration-display').text(`Équivaut à: ${durationText}`);
        } else {
            $('#contract-duration-display').text('');
        }
    });
});
