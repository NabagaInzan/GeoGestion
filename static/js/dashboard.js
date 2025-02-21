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
                const canvas = document.createElement('canvas');
                canvas.width = this.width;
                canvas.height = this.height;
                const ctx = canvas.getContext('2d');
                ctx.drawImage(this, 0, 0);
                resolve(canvas.toDataURL('image/jpeg'));
            };
            img.onerror = reject;
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
                        customize: async function (doc) {
                            // Chargement des images
                            const backgroundImage = await getBase64FromImageUrl('/static/images/operateur.jpeg');
                            const logoImage = await getBase64FromImageUrl('/static/images/logo.png');

                            // Style du document
                            doc.pageMargins = [40, 100, 40, 40];
                            doc.defaultStyle = {
                                font: 'Roboto',
                                fontSize: 10
                            };

                            // Ajout du fond d'écran avec opacité
                            doc.background = {
                                image: backgroundImage,
                                width: 595.28, // A4 width
                                opacity: 0.1
                            };

                            // En-tête avec logo
                            doc.header = {
                                columns: [
                                    {
                                        image: logoImage,
                                        width: 100,
                                        alignment: 'left',
                                        margin: [40, 20, 0, 0]
                                    },
                                    {
                                        text: 'GeoGestion AFOR\nListe des Employés',
                                        alignment: 'right',
                                        margin: [0, 20, 40, 0],
                                        fontSize: 16,
                                        bold: true,
                                        color: '#059669'
                                    }
                                ]
                            };

                            // Pied de page
                            doc.footer = function(currentPage, pageCount) {
                                return {
                                    columns: [
                                        {
                                            text: 'Généré le ' + new Date().toLocaleDateString('fr-FR', {
                                                day: '2-digit',
                                                month: 'long',
                                                year: 'numeric',
                                                hour: '2-digit',
                                                minute: '2-digit'
                                            }),
                                            alignment: 'left',
                                            margin: [40, 0, 0, 0],
                                            fontSize: 8
                                        },
                                        {
                                            text: 'Page ' + currentPage + ' sur ' + pageCount,
                                            alignment: 'right',
                                            margin: [0, 0, 40, 0],
                                            fontSize: 8
                                        }
                                    ]
                                };
                            };

                            // Style du tableau
                            doc.styles.tableHeader = {
                                fillColor: '#059669',
                                color: '#ffffff',
                                bold: true,
                                fontSize: 11,
                                alignment: 'left'
                            };

                            doc.styles.tableBodyEven = {
                                fillColor: '#f3f4f6'
                            };

                            // Ajout d'une bordure autour du tableau
                            doc.content[0].table.layout = {
                                hLineWidth: function(i, node) { return 1; },
                                vLineWidth: function(i, node) { return 1; },
                                hLineColor: function(i, node) { return '#e5e7eb'; },
                                vLineColor: function(i, node) { return '#e5e7eb'; },
                                paddingLeft: function(i, node) { return 8; },
                                paddingRight: function(i, node) { return 8; },
                                paddingTop: function(i, node) { return 6; },
                                paddingBottom: function(i, node) { return 6; }
                            };
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
            url: '/api/employees',
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
        $.get('/api/stats')
            .done(function(response) {
                if (response.success) {
                    const stats = response.stats;
                    
                    // Mise à jour du total des employés
                    $('.total-employees').text(stats.total_employees);
                    
                    // Mise à jour de la répartition homme/femme
                    const men = stats.gender_distribution['M'] || 0;
                    const women = stats.gender_distribution['F'] || 0;
                    $('.gender-stats').text(`${men}/${women}`);
                    
                    // Mise à jour des contrats actifs
                    const activeContracts = (stats.contract_distribution['CDI'] || 0) + 
                                         (stats.contract_distribution['CDD'] || 0);
                    $('.contract-stats').text(activeContracts);
                    
                    // Mise à jour des employés disponibles
                    $('.availability-stats').text(stats.availability_distribution['Disponible'] || 0);
                }
            })
            .fail(function(xhr) {
                console.error('Erreur lors du chargement des statistiques:', xhr.responseText);
            });
    }

    // Charger les statistiques au démarrage
    loadStats();

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
        
        // Confirmation de suppression avec Bootstrap modal
        if (confirm('Êtes-vous sûr de vouloir supprimer cet employé ?')) {
            // Afficher le loader
            $('.loader').show();
            
            // Envoyer la requête de suppression
            $.ajax({
                url: `/api/employees/${employeeId}`,
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
        
        // Afficher le loader
        $('.loader').show();
        
        // Récupérer les données du formulaire
        const formData = new FormData(this);
        const jsonData = {};
        
        // Convertir FormData en objet JSON
        formData.forEach((value, key) => {
            jsonData[key] = value;
        });
        
        // Déterminer l'URL et la méthode en fonction de l'action (ajout ou modification)
        const url = currentEmployeeId ? `/api/employees/${currentEmployeeId}` : '/api/employees';
        const method = currentEmployeeId ? 'PUT' : 'POST';
        
        // Envoyer la requête
        $.ajax({
            url: url,
            method: method,
            data: JSON.stringify(jsonData),
            contentType: 'application/json',
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
                    showToast('Employé ' + (method === 'PUT' ? 'modifié' : 'ajouté') + ' avec succès', 'fas fa-check-circle');
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
