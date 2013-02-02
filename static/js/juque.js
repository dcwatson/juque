$(function() {
    var cls = 'li.nav-' + $('body').attr('class');
    $(cls).addClass('active');

    $('select').chosen();

    if(initial_field) {
        $('#' + initial_field).focus().select();
    }
});
