$(document).ready(function() {

    $(document).on('click', '.hamburger-menu', function(event) {

        event.preventDefault();

        var action = $(this).attr('id');

        req = $.ajax({
            url : '/ham_menu',
            type : 'POST',
            data : { action : action }
        });

        req.done(function(data) {
            $('.ham-menu').html(data);
        });

    });

});