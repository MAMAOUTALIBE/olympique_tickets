$(function () {
    $("#adminTable").DataTable({
        "responsive": true, "lengthChange": true, "autoWidth": false, "ordering": true, "order": [],
        "language": {
            emptyTable: "Aucun " + dataSubTitle + " disponible",
            info: "Affichage de " + dataSubTitle + " _START_ à _END_ sur _TOTAL_ " + dataTitle,
            infoEmpty: "Affichage de l'élément 0 à 0 sur 0 élément",
            infoFiltered: "(filtré à partir de _MAX_ éléments au total)",
            infoThousands: ",",
            lengthMenu: 'Afficher <select class=\'custom-select custom-select-sm ml-1 mr-1\'><option value="10">10</option><option value="20">20</option><option value="-1">Tout</option></select> ' + dataTitle,
            pageLength: 10,
            loadingRecords: "Chargement...",
            processing: "Traitement...",
            search: "Rechercher :",
            zeroRecords: "Aucun " + dataSubTitle + " correspondant trouvé",
            paginate: { previous: "<i class='bi bi-chevron-left'>", next: "<i class='bi bi-chevron-right'>" },

        },
    }).buttons().container().appendTo('#example1_wrapper .col-md-6:eq(0)');

});