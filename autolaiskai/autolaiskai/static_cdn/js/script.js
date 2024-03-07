/* Used in landing.html, then page active change tag color*/
$('#ClickMe li a').on('click', function() {
    $('#ClickMe li a.active').removeClass('active');
    $(this).addClass('active');
});

$('form .autosubmit').on('change', function() {
    this.form.submit();
    console.log("form submitted!")
});