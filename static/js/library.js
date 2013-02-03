function load_page(query) {
    $.ajax({
        url: page_url,
        data: query || {},
        dataType: 'html',
        success: function(html) {
            $('#page').empty().append(html);
            $('#q').val(query.q || '');
        }
    });
}

function show_alert(msg, type) {
    type = type || '';
    var close = '<a href="#" class="close" data-dismiss="alert">&times;</a>';
    var html = '<div class="alert alert-' + type + '"><strong>' + type.toUpperCase() + '</strong> ' + msg + close + '</div>';
    $('#message').append(html);
}

$(function() {
    $('body').on('click', 'a.filter', function(e) {
        var query = $(this).data('query');
        load_page(query);
        return false;
    });

    $('body').on('click', 'a.play', function(e) {
        var url = $(this).data('track-url');
        var id = $(this).data('track-id');
        $('div.player img').attr('src', $(this).data('cover-url'));
        $('div.player .track').text($(this).data('title'));
        $('div.player .artist').text($(this).data('artist'));
        var player = document.getElementById('player');
        $(player).attr('src', url);
        player.play();

        $.ajax({
            url: '/library/ajax/play/' + id + '/'
        });

        return false;
    });

    $('body').on('click', 'a.playlist-add', function(e) {
        $.ajax({
            url: playlist_add_url,
            data: {
                track: $(this).data('track'),
                playlist: $(this).data('playlist')
            },
            dataType: 'json',
            success: function(data) {
                show_alert(data.message, data.type);
            }
        });
    });

    $('#search-form').submit(function() {
        load_page({q: $('#q').val()});
        return false;
    });

    load_page({q: $('#q').val()});
});
