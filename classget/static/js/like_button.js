$(document).ready(function() {


    $(document).on('click', ".user_like_button", function(event) {

        event.preventDefault();

        var request_id = $(this).attr('id').split('_');
        var subject_id = request_id[1];
        var action = request_id[0];

        req = $.ajax({
            url : '/like',
            type : 'POST',
            data : { subject_id : subject_id, action : action }
        });

        req.done(function(data) {
            $('.like_buttons'+subject_id).html(data);
        });

    });



});