var $selectStatus = $(".status").selectize({sortField:"text",hideSelected:!1,plugins:{dropdown_header:{title:"Statut"}}});

$(function () {
    $("#userTable").DataTable({
      "responsive": true, "lengthChange": true, "autoWidth": false, "ordering": true, "order": [],
      "language": {
          emptyTable: "Aucun "+singleSubTitle+" disponible",
          info: "Affichage de "+singleSubTitle+" _START_ à _END_ sur _TOTAL_ "+singleSubTitle+"s",
          infoEmpty: "Affichage de l'élément 0 à 0 sur 0 élément",
          infoFiltered: "(filtré à partir de _MAX_ éléments au total)",
          infoThousands: ",",
          lengthMenu: 'Afficher <select class=\'custom-select custom-select-sm ml-1 mr-1\'><option value="10">10</option><option value="20">20</option><option value="-1">Tout</option></select> '+singleSubTitle+'s',
          pageLength:10,
          loadingRecords: "Chargement...",
          processing: "Traitement...",
          search: "Rechercher :",
          zeroRecords: "Aucun "+singleSubTitle+" correspondant trouvé",
          paginate:{previous:"<i class='bi bi-chevron-left'>",next:"<i class='bi bi-chevron-right'>"},

      },
    }).buttons().container().appendTo('#example1_wrapper .col-md-6:eq(0)');


  });

function createModal(){
    jQuery('#modalCreateEdit').modal('show',{backdrop:'static',keyboard:false});
    $('#modalCreateEditTitle').text("Ajouter un nouveau " + singleSubTitle);
    $('#modalCreateEditSubmitBtn').text("Enregistrer");
    $('#modalCreateEditForm')[0].reset();
    $('#id').val("");
    $(".check_pass").hide();
}

function updateModal(id){
    $('#modalCreateEditTitle').text("Modification " + singleSubTitle);
    $('#modalCreateEditSubmitBtn').text("Modifier");
    $('#id').val(id);
    $(".check_pass").show();

    $.post(getUserUrl, {"id": id},
        function (data, textStatus, jqXHR) {
            console.log(data.data);
            if(data.status == 200){
                var agencyData = data.data.agency;

                
                $("#username").val(data.data.user.username);
                $("#first_name").val(data.data.user.first_name);
                $("#last_name").val(data.data.user.last_name);
                $("#email").val(data.data.user.email);
                $("#phone").val(data.data.user.phone);

                if (role == 'agency' && agencyData != null) {
                    $("#city").val(agencyData.city);
                    $("#state").val(agencyData.state);
                    $("#postal_code").val(agencyData.postal_code);
                    $("#longitude").val(agencyData.longitude);
                    $("#latitude").val(agencyData.latitude);
                    $("#agency_code").val(agencyData.code);
                }
                jQuery('#modalCreateEdit').modal('show',{backdrop:'static',keyboard:false});
            }else{
                errorToast(data.message);
            }
        },
        "Json"
    );
}

function createUpdateUser() {

    var data = {
        "id": $("#id").val(),
        "agency_code": $("#agency_code").val(),
        "first_name": $("#first_name").val(),
        "last_name": $("#last_name").val(),
        "email": $("#email").val(),
        "phone": $("#phone").val(),
        //Ajout du agency
        "city": $("#city").val(),
        "state": $("#state").val(),
        "postal_code": $("#postal_code").val(),
        "longitude": $("#longitude").val(),
        "latitude": $("#latitude").val(),
        //Fin AJout de agency
        "password": $("#password").val(),
        "confirmPassword": $("#confirmPassword").val(),
        "default_role": role,
        "canUpdatePassword": $('#checkbox-update-password').is(":checked")
    };
    $(".createBtn").hide();
    $(".loadingBtn").show();
    $.ajax({
        url: createUpdateUserUrl,
        type: "POST",
        data: data,
        dataType: "JSON",
        success: function (data) {
            $(".createBtn").show();
            $(".loadingBtn").hide();
            if(data.status == 200){
                successToast(data.message);
                setTimeout(function(){location.reload(true);}, 1000);
            }else{
                errorToast(data.message);
            }
        },
        error: function (jqXHR, textStatus, errorThrown) {
            console.log(jqXHR);
            console.log(textStatus);
            console.log(errorThrown);
        }
    });
}

function deleteUser(id, name) {
    Swal.fire({
        title: 'Voulez-vous vraiment supprimer l\'utilisateur '+name+' ?',
        icon: 'error',
        showDenyButton: false,
        showCancelButton: true,
        confirmButtonText: 'Supprimer',
        denyButtonText: 'Annuler',
        cancelButtonText: 'Annuler',
        confirmButtonColor: '#d33',
        cancelButtonColor: '#595757',
        }).then((result) => {
        if (result.isConfirmed) {
            $.post(deleteUserUrl, {"id": id},
                function (data, textStatus, jqXHR) {
                    if(data.status == 200){
                        successToast(data.message);
                        setTimeout(function(){location.reload(true);}, 1000);
                    }else{
                        errorToast(data.message);
                    }
                },
                "Json"
            );
        }
    });
}


function activateData(id) {
    Swal.fire({
        title: 'Voulez-vous activer l\'utilisateur ?',
        icon: 'warning',
        showDenyButton: false,
        showCancelButton: true,
        confirmButtonText: 'Activer',
        denyButtonText: 'Annuler',
        cancelButtonText: 'Annuler',
        confirmButtonColor: '#d33',
        cancelButtonColor: '#595757',
        }).then((result) => {
        if (result.isConfirmed) {
            $.post(activateUrl, {"id": id},
                function (data, textStatus, jqXHR) {
                    if(data.status == 200){
                        successToast(data.message);
                        setTimeout(function(){location.reload(true);}, 1000);
                    }else{
                        errorToast(data.message);
                    }
                },
                "Json"
            );
        }
    });
}



function deActivateData(id) {
    Swal.fire({
        title: 'Voulez-vous vraiment désactiver l\'utilisateur ?',
        icon: 'warning',
        showDenyButton: false,
        showCancelButton: true,
        confirmButtonText: 'Désactiver',
        denyButtonText: 'Annuler',
        cancelButtonText: 'Annuler',
        confirmButtonColor: '#d33',
        cancelButtonColor: '#595757',
        }).then((result) => {
        if (result.isConfirmed) {
            $.post(deActivateUrl, {"id": id},
                function (data, textStatus, jqXHR) {
                    if(data.status == 200){
                        successToast(data.message);
                        setTimeout(function(){location.reload(true);}, 1000);
                    }else{
                        errorToast(data.message);
                    }
                },
                "Json"
            );
        }
    });
}

function createModalInfo(){
    jQuery('#modalCompleteInfos').modal('show',{backdrop:'static',keyboard:false});
    $('#modalCompleteInfosTitle').text("Compléter vos informations");
    $('#modalCompleteInfosSubmitBtn').text("Enregistrer");
    $('#modalCompleteInfosForm')[0].reset();
}

function completeInfosUser() {

    var formData = new FormData();

    formData.append("id", $("#idUser").val());
    formData.append("first_name", $("#first_name").val());
    formData.append("last_name", $("#last_name").val());
    formData.append("phone", $("#get_phone").val());
    formData.append("email", $("#get_email").val());
    formData.append("username", $("#get_username").val());
    formData.append("adress", $("#adress").val());
    formData.append("country_name", $("#country_name").val());
    formData.append("birth_date", $("#birth_date").val());
    formData.append("sexe", $("#get_sexe").val());
    formData.append("country_name", $("#get_country_name").val());
    formData.append("profil_image", $("#profil_image")[0].files[0]);

    $(".createBtn").hide();
    $(".loadingBtn").show();
    $.ajax({
        url: completeInfosrUrl,
        type: "POST",
        data: formData,
        processData: false,
        contentType: false,
        dataType: "JSON",
        success: function (data) {
            $(".createBtn").show();
            $(".loadingBtn").hide();
            if(data.status == 200){
                successToast(data.message);
                setTimeout(function(){location.reload(true);}, 1000);
            }else{
                errorToast(data.message);
            }
        },
        error: function (jqXHR, textStatus, errorThrown) {
            console.log(jqXHR);
            console.log(textStatus);
            console.log(errorThrown);
        }
    });
}


//Change password request
function changepasswordData() {

    var data = {
        "id": $("#id").val(),
        "old_password": $("#old_password").val(),
        "new_password": $("#new_password").val(),
        "confirm_password": $("#confirm_password").val(),
    };

    $(".createBtn").hide();
    $(".loadingBtn").show();
    $.ajax({
        url: changepasswordUrl,
        type: "POST",
        data: data,
        dataType: "JSON",
        success: function (data) {
            $(".createBtn").show();
            $(".loadingBtn").hide();
            if(data.status == 200){
                successToast(data.message);
                setTimeout(function(){location.reload(true);}, 1000);
            }else{
                errorToast(data.message);
            }
        },
        error: function (jqXHR, textStatus, errorThrown) {
            console.log(jqXHR);
            console.log(textStatus);
            console.log(errorThrown);
        }
    });
}

