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

$(function() {
    $('body').on('click', 'a.filter', function(e) {
        var query = $(this).data('query');
        load_page(query);
        return false;
    });

    $('body').on('click', 'a.play', function() {
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

    $('#search-form').submit(function() {
        load_page({q: $('#q').val()});
        return false;
    });

    load_page({q: $('#q').val()});
});
