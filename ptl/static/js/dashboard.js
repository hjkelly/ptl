$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        function getCookie(name) {
            var cookieValue = null;
            if (document.cookie && document.cookie != '') {
                var cookies = document.cookie.split(';');
                for (var i = 0; i < cookies.length; i++) {
                    var cookie = jQuery.trim(cookies[i]);
                    // Does this cookie string begin with the name we want?
                    if (cookie.substring(0, name.length + 1) == (name + '=')) {
                        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                        break;
                    }
                }
            }
            return cookieValue;
        }
        if (!(/^http:.*/.test(settings.url) || /^https:.*/.test(settings.url))) {
            // Only send the token to relative URLs i.e. locally.
            xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
        }
    }
});

function showOrHideAddAnother() {
    if ($('.partners li').length >= 3) {
        $('.another').hide();
    } else {
        $('.another').show();
    }
}

$('.partners').on('click', '.remove', function (ev) {
    alert('removing!');
    // Don't follow the link; that's not helpful.
    ev.preventDefault();
    // Submit a DELETE request.
    var elementToBeDeleted = $(this).parentsUntil('.partners');
    $.ajax({
        type: "DELETE",
        url: $(this).attr('href'),
        success: function (data, textStatus, jqXHR) {
            elementToBeDeleted.remove();
        }
    });
});

$('.another').submit(function (ev) {
    alert('adding!');
    // Don't submit. That's not helpful.
    ev.preventDefault();
    // Put together the POST data.
    var elements = $(this).serializeArray();
    var data = {};
    for (var i in elements) {
        data[elements[i].name] = elements[i].value;
    }
    $.ajax({
        type: "POST",
        url: addAnotherUrl,
        data: data,
        success: function (data, textStatus, jqXHR) {
            $('.partners').append(
                '<li>' +
                    data.name + ' &mdash; ' +
                    data.phone_number + ' &mdash; ' +
                    '<a href="' + data.url + '">Remove</a> &mdash; ' +
                '</li>');
        }
    });
});
