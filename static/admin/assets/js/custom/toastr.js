var Toast = Swal.mixin({
    toast: true,
    position: 'top-end',
    showConfirmButton: false,
    timer: 3000
  });


function successToast(message) {
    Swal.fire(
      'Succès!',
      message,
      'success'
    )
}

function errorToast(message) {
    Swal.fire(
      'Erreur!',
      message,
      'error'
    )
}