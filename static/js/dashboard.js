// Gestionnaire d'erreur global pour les requêtes AJAX
$(document).ajaxError(function(event, jqXHR, settings, error) {
    if (jqXHR.status === 401) {
        // Redirection vers la page de connexion
        window.location.href = '/';
    }
});

$(document).ready(function() {
    // Initialisation des variables
    let employeesTable;
    let currentEmployeeId = null;

    // Fonction pour convertir une image en base64
    function getBase64FromImageUrl(url) {
        return new Promise((resolve, reject) => {
            const img = new Image();
            img.crossOrigin = 'Anonymous';
            img.onload = function () {
                try {
                    const canvas = document.createElement('canvas');
                    canvas.width = this.width;
                    canvas.height = this.height;
                    const ctx = canvas.getContext('2d');
                    ctx.drawImage(this, 0, 0);
                    resolve(canvas.toDataURL('image/jpeg').split(',')[1]);
                } catch (error) {
                    console.error('Erreur lors de la conversion de l\'image:', error);
                    reject(error);
                }
            };
            img.onerror = function(error) {
                console.error('Erreur lors du chargement de l\'image:', error);
                reject(error);
            };
            img.src = url;
        });
    }

    // Configuration de pdfmake pour le français
    pdfMake.fonts = {
        Roboto: {
            normal: 'https://cdnjs.cloudflare.com/ajax/libs/pdfmake/0.2.7/fonts/Roboto/Roboto-Regular.ttf',
            bold: 'https://cdnjs.cloudflare.com/ajax/libs/pdfmake/0.2.7/fonts/Roboto/Roboto-Medium.ttf',
            italics: 'https://cdnjs.cloudflare.com/ajax/libs/pdfmake/0.2.7/fonts/Roboto/Roboto-Italic.ttf',
            bolditalics: 'https://cdnjs.cloudflare.com/ajax/libs/pdfmake/0.2.7/fonts/Roboto/Roboto-MediumItalic.ttf'
        }
    };

    // Initialisation de DataTables
    employeesTable = $('#employeesTable').DataTable({
        language: {
            processing: "Traitement en cours...",
            search: "Rechercher&nbsp;:",
            lengthMenu: "Afficher _MENU_ éléments",
            info: "Affichage de _START_ à _END_ sur _TOTAL_ éléments",
            infoEmpty: "Affichage de 0 à 0 sur 0 élément",
            infoFiltered: "(filtré de _MAX_ éléments au total)",
            infoPostFix: "",
            loadingRecords: "Chargement en cours...",
            zeroRecords: "Aucun élément à afficher",
            emptyTable: "Aucune donnée disponible",
            paginate: {
                first: "Premier",
                previous: "Précédent",
                next: "Suivant",
                last: "Dernier"
            },
            aria: {
                sortAscending: ": activer pour trier la colonne par ordre croissant",
                sortDescending: ": activer pour trier la colonne par ordre décroissant"
            },
            buttons: {
                copy: "Copier",
                print: "Imprimer",
                excel: "Excel",
                pdf: "PDF",
                colvis: "Colonnes",
                pageLength: "Afficher _MENU_ éléments"
            }
        },
        dom: '<"row"<"col-sm-12 col-md-6"B><"col-sm-12 col-md-6"f>>rt<"row"<"col-sm-12 col-md-6"l><"col-sm-12 col-md-6"p>>',
        buttons: [
            {
                extend: 'collection',
                text: '<i class="fas fa-file-export"></i> Exporter',
                className: 'btn-success',
                buttons: [
                    {
                        extend: 'excel',
                        text: '<i class="fas fa-file-excel"></i> Excel',
                        className: 'btn-success',
                        exportOptions: {
                            columns: ':visible'
                        }
                    },
                    {
                        extend: 'pdf',
                        text: '<i class="fas fa-file-pdf"></i> PDF',
                        className: 'btn-danger',
                        exportOptions: {
                            columns: ':visible'
                        },
                        customize: function (doc) {
                            try {
                                // Définition des styles de base
                                doc.styles = {
                                    header: {
                                        fontSize: 18,
                                        bold: true,
                                        color: '#059669'
                                    },
                                    subheader: {
                                        fontSize: 14,
                                        bold: true,
                                        color: '#4B5563'
                                    },
                                    tableHeader: {
                                        bold: true,
                                        fontSize: 11,
                                        color: 'white',
                                        fillColor: '#059669',
                                        alignment: 'left'
                                    },
                                    defaultStyle: {
                                        fontSize: 10,
                                        color: '#4B5563'
                                    }
                                };

                                // Configuration de la page
                                doc.pageMargins = [40, 100, 40, 40];
                                doc.pageOrientation = 'landscape';

                                // En-tête avec logo
                                const logoUrl = '/static/images/logo.png';
                                const img = new Image();
                                img.src = logoUrl;

                                // Attendre que l'image soit chargée
                                img.onload = function() {
                                    const canvas = document.createElement('canvas');
                                    const ctx = canvas.getContext('2d');
                                    canvas.width = img.width;
                                    canvas.height = img.height;
                                    ctx.drawImage(img, 0, 0);
                                    const imageData = canvas.toDataURL('image/png');

                                    // Ajouter le logo et le titre
                                    doc.content.unshift({
                                        columns: [
                                            {
                                                image: imageData,
                                                width: 100,
                                                alignment: 'left'
                                            },
                                            {
                                                text: 'GeoGestion AFOR - Liste des Employés',
                                                style: 'header',
                                                alignment: 'center',
                                                margin: [0, 20, 0, 0]
                                            }
                                        ],
                                        margin: [40, 20, 40, 20]
                                    });
                                };

                                img.onerror = function() {
                                    console.warn("Impossible de charger le logo");
                                    // Ajouter uniquement le titre si le logo ne peut pas être chargé
                                    doc.content.unshift({
                                        text: 'GeoGestion AFOR - Liste des Employés',
                                        style: 'header',
                                        alignment: 'center',
                                        margin: [0, 20, 0, 20]
                                    });
                                };

                                // Vérifions que le tableau existe
                                const tableIndex = doc.content.findIndex(item => item.table);
                                if (tableIndex !== -1) {
                                    // Configuration du tableau
                                    const table = doc.content[tableIndex].table;
                                    
                                    // Définir la largeur des colonnes
                                    table.widths = [
                                        '*', // Nom
                                        '*', // Prénom
                                        'auto', // Position
                                        'auto', // Contact
                                        'auto', // Genre
                                        'auto', // Disponibilité
                                        'auto'  // Actions
                                    ];

                                    // Style des en-têtes
                                    if (table.body && table.body[0]) {
                                        table.headerRows = 1;
                                        table.body[0].forEach(cell => {
                                            cell.fillColor = '#059669';
                                            cell.color = '#FFFFFF';
                                            cell.fontSize = 11;
                                            cell.bold = true;
                                            cell.margin = [5, 7, 5, 7];
                                        });

                                        // Style des cellules
                                        for (let i = 1; i < table.body.length; i++) {
                                            table.body[i].forEach(cell => {
                                                cell.fontSize = 10;
                                                cell.margin = [5, 5, 5, 5];
                                            });
                                        }
                                    }

                                    // Style du tableau
                                    table.layout = {
                                        hLineWidth: function(i, node) { 
                                            return (i === 0 || i === node.table.body.length) ? 1 : 0.5;
                                        },
                                        vLineWidth: function(i, node) { 
                                            return 0.5;
                                        },
                                        hLineColor: function(i, node) {
                                            return (i === 0 || i === node.table.body.length) ? '#059669' : '#E5E7EB';
                                        },
                                        vLineColor: function(i, node) {
                                            return '#E5E7EB';
                                        },
                                        paddingLeft: function(i) { return 8; },
                                        paddingRight: function(i) { return 8; },
                                        paddingTop: function(i) { return 6; },
                                        paddingBottom: function(i) { return 6; },
                                        fillColor: function(rowIndex, node, columnIndex) {
                                            return (rowIndex % 2 === 1) ? '#F9FAFB' : null;
                                        }
                                    };
                                }

                                // Pied de page avec date et nombre d'employés
                                const footer = {
                                    columns: [
                                        {
                                            text: `Généré le ${new Date().toLocaleDateString('fr-FR', {
                                                weekday: 'long',
                                                year: 'numeric',
                                                month: 'long',
                                                day: 'numeric',
                                                hour: '2-digit',
                                                minute: '2-digit'
                                            })}`,
                                            style: 'defaultStyle',
                                            alignment: 'left',
                                            width: '*'
                                        },
                                        {
                                            text: `Nombre total d'employés : ${doc.content[tableIndex].table.body.length - 1}`,
                                            style: 'subheader',
                                            alignment: 'right',
                                            width: 'auto'
                                        }
                                    ],
                                    margin: [40, 20, 40, 0]
                                };

                                // Ajouter le pied de page
                                doc.content.push(footer);

                            } catch (error) {
                                console.error('Erreur lors de la personnalisation du PDF:', error);
                            }
                        }
                    },
                    {
                        extend: 'print',
                        text: '<i class="fas fa-print"></i> Imprimer',
                        className: 'btn-info',
                        exportOptions: {
                            columns: ':visible'
                        }
                    }
                ]
            },
            {
                extend: 'colvis',
                text: '<i class="fas fa-columns"></i> Colonnes',
                className: 'btn-secondary'
            },
            {
                text: '<i class="fas fa-sync"></i> Actualiser',
                className: 'btn-primary',
                action: function (e, dt, node, config) {
                    dt.ajax.reload(null, false);
                    showToast('Données actualisées', 'fas fa-sync-alt');
                }
            },
            {
                text: '<i class="fas fa-expand"></i>',
                className: 'btn-dark',
                action: function (e, dt, node, config) {
                    if (!document.fullscreenElement) {
                        document.documentElement.requestFullscreen();
                        node.html('<i class="fas fa-compress"></i>');
                    } else {
                        document.exitFullscreen();
                        node.html('<i class="fas fa-expand"></i>');
                    }
                }
            }
        ],
        responsive: true,
        colReorder: true,
        fixedHeader: {
            header: true,
            headerOffset: $('.navbar').height()
        },
        ajax: {
            url: config.apiBaseUrl + '/api/employees',
            dataSrc: ''
        },
        columns: [
            { data: 'last_name' },
            { data: 'first_name' },
            { data: 'position' },
            { data: 'contact' },
            { data: 'gender' },
            { data: 'availability' },
            {
                data: null,
                render: function(data, type, row) {
                    return `
                        <div class="btn-group" role="group">
                            <button class="btn btn-sm btn-info edit-btn me-2" data-id="${row.id}" title="Modifier">
                                <i class="fas fa-edit"></i>
                            </button>
                            <button class="btn btn-sm btn-danger delete-btn" data-id="${row.id}" title="Supprimer">
                                <i class="fas fa-trash"></i>
                            </button>
                        </div>
                    `;
                }
            }
        ]
    });

    // Charger les statistiques
    function loadStats() {
        $('.stats-loader').show(); // Ajout d'un indicateur de chargement
        
        $.ajax({
            url: config.apiBaseUrl + '/api/stats',
            method: 'GET',
            success: function(response) {
                if (response && response.success) {
                    const stats = response.stats;
                    
                    // Mise à jour du total des employés
                    const totalEmployees = stats.total_employees || 0;
                    $('.total-employees').text(totalEmployees);
                    
                    // Mise à jour de la répartition homme/femme
                    const men = stats.gender_distribution ? (stats.gender_distribution['M'] || 0) : 0;
                    const women = stats.gender_distribution ? (stats.gender_distribution['F'] || 0) : 0;
                    $('.gender-stats').text(`${men}/${women}`);
                    
                    // Mise à jour des contrats actifs
                    const activeContracts = stats.contract_distribution ? (stats.contract_distribution.active || 0) : 0;
                    $('.contract-stats').text(activeContracts);
                    
                    // Mise à jour des employés disponibles
                    let availableEmployees = 0;
                    if (stats.availability_distribution && stats.availability_distribution['Disponible']) {
                        availableEmployees = stats.availability_distribution['Disponible'];
                    }
                    $('.availability-stats').text(availableEmployees);
                    
                    // Afficher un message de succès discret
                    showToast('Statistiques mises à jour avec succès', 'fas fa-chart-bar');
                } else {
                    console.error('Format de réponse invalide:', response);
                    showToast('Erreur lors de la mise à jour des statistiques: données invalides', 'fas fa-exclamation-triangle');
                    resetStats();
                }
            },
            error: function(xhr, status, error) {
                console.error('Erreur lors du chargement des statistiques:', error);
                showToast('Erreur de connexion lors de la mise à jour des statistiques', 'fas fa-exclamation-triangle');
                resetStats();
            },
            complete: function() {
                $('.stats-loader').hide();
            }
        });
    }

    // Fonction pour réinitialiser les statistiques
    function resetStats() {
        $('.total-employees').text('--');
        $('.gender-stats').text('--/--');
        $('.contract-stats').text('--');
        $('.availability-stats').text('--');
    }

    // Charger les statistiques au démarrage
    loadStats();

    // Rafraîchir les statistiques toutes les 60 secondes
    setInterval(loadStats, 60000);

    // Rafraîchir les statistiques après chaque modification d'employé
    function refreshStats() {
        setTimeout(loadStats, 1000); // Délai d'une seconde pour laisser le temps à la base de données de se mettre à jour
    }

    // Gestionnaire pour le bouton d'ajout
    $('#addEmployeeBtn').click(function() {
        currentEmployeeId = null;
        $('#employeeModal').modal('show');
        $('#employeeForm')[0].reset();
        $('.modal-title').text('Ajouter un Employé');
    });

    // Gestionnaire pour le bouton de modification
    $('#employeesTable').on('click', '.edit-btn', function() {
        const employeeId = $(this).data('id');
        
        // Afficher le loader
        $('.loader').show();
        
        // Récupérer les données de l'employé
        $.get(`/api/employees/${employeeId}`)
            .done(function(response) {
                // Vérifier si la réponse contient les données de l'employé
                const employee = response.employee || response.data;
                
                if (employee) {
                    // Remplir le formulaire avec les données
                    $('#firstName').val(employee.first_name || '');
                    $('#lastName').val(employee.last_name || '');
                    $('#position').val(employee.position || '');
                    $('#contact').val(employee.contact || '');
                    $('#gender').val(employee.gender || '');
                    $('#contractDuration').val(employee.contract_duration || '');
                    $('#birthDate').val(employee.birth_date || '');
                    $('#availability').val(employee.availability || '');
                    $('#salary').val(employee.salary || '');
                    $('#additionalInfo').val(employee.additional_info || '');
                    
                    // Stocker l'ID de l'employé en cours d'édition
                    currentEmployeeId = employeeId;
                    
                    // Mettre à jour le titre du modal
                    $('.modal-title').html('<i class="fas fa-user-edit me-2"></i>Modifier un Employé');
                    
                    // Mettre à jour le texte du bouton de soumission
                    $('#submitEmployeeBtn').html('<i class="fas fa-save me-2"></i>Enregistrer les modifications');
                    
                    // Afficher le modal
                    $('#addEmployeeModal').modal('show');
                    
                    // Recalculer l'âge si la date de naissance est présente
                    if (employee.birth_date) {
                        calculateAge();
                    }
                } else {
                    showToast('Erreur : Données de l\'employé non trouvées', 'fas fa-times-circle');
                }
            })
            .fail(function(xhr) {
                showToast('Erreur de connexion au serveur : ' + (xhr.responseJSON?.message || 'Erreur inconnue'), 'fas fa-times-circle');
            })
            .always(function() {
                $('.loader').hide();
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
                url: config.apiBaseUrl + `/api/employees/${employeeId}`,
                method: 'DELETE',
                success: function(response) {
                    if (response.success) {
                        // Actualiser le tableau
                        employeesTable.ajax.reload();
                        showToast('Employé supprimé avec succès', 'fas fa-check-circle');
                    } else {
                        showToast('Erreur lors de la suppression', 'fas fa-times-circle');
                    }
                },
                error: function() {
                    showToast('Erreur de connexion au serveur', 'fas fa-times-circle');
                },
                complete: function() {
                    $('.loader').hide();
                }
            });
        }
    });

    // Gestionnaire de soumission du formulaire
    $('#addEmployeeForm').on('submit', function(e) {
        e.preventDefault();
        const formData = new FormData(this);
        
        $.ajax({
            url: config.apiBaseUrl + '/api/employees',
            method: 'POST',
            data: formData,
            processData: false,
            contentType: false,
            success: function(response) {
                if (response.success) {
                    // Fermer le modal
                    $('#addEmployeeModal').modal('hide');
                    
                    // Actualiser le tableau
                    employeesTable.ajax.reload();
                    
                    // Réinitialiser le formulaire
                    $('#addEmployeeForm')[0].reset();
                    currentEmployeeId = null;
                    
                    // Afficher le message de succès
                    showToast('Employé ajouté avec succès', 'fas fa-check-circle');
                } else {
                    showToast('Erreur lors de l\'opération', 'fas fa-times-circle');
                }
            },
            error: function(xhr) {
                showToast('Erreur : ' + (xhr.responseJSON?.message || 'Erreur inconnue'), 'fas fa-times-circle');
            },
            complete: function() {
                $('.loader').hide();
            }
        });
    });

    // Rafraîchir les données toutes les 30 secondes
    setInterval(function() {
        employeesTable.ajax.reload();
        loadStats();
    }, 30000);
});
