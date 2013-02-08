var last_query = {};

function load_page(query) {
    query = query || last_query;
    $.ajax({
        url: page_url,
        data: query || {},
        dataType: 'html',
        success: function(html) {
            $('#page').empty().append(html);
            $('#q').val(query.q || '');
            last_query = query;
        }
    });
}

function show_alert(msg, alert_type) {
    alert_type = alert_type || 'success';
    var close = '<a href="#" class="close" data-dismiss="alert">&times;</a>';
    var html = '<div class="alert alert-' + alert_type + '">' + msg + close + '</div>';
    $('#message').append(html);
}

function update_select_all() {
    $('input.track-select:checked').length > 0 ? btn.removeClass('disabled') : btn.addClass('disabled');

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

        $('div.artwork img').attr('src', $(this).data('cover-url'));
        $('div.artwork .track').text($(this).data('title'));
        $('div.artwork .artist').text($(this).data('artist'));

        var player = document.getElementById('player');
        $(player).attr('src', url);
        player.play();

        $.ajax({
            url: '/library/ajax/play/' + id + '/'
        });

        return false;
    });

    $('body').on('click', 'a.playlist-add', function(e) {
        var tracks = [];
        $('input.track-select:checked').each(function(idx, elem) {
            tracks.push($(elem).val());
        });
        $.ajax({
            url: $(this).attr('href'),
            data: {
                tracks: tracks,
                playlist: $(this).data('playlist')
            },
            dataType: 'json',
            traditional: true,
            success: function(data) {
                $('#track-select').dropdown('toggle');
                show_alert(data.message);
            }
        });
        return false;
    });

    $('body').on('click', 'a.playlist-create', function(e) {
        var url = $(this).attr('href');
        $('input.track-select:checked').each(function(idx, elem) {
            var ch = idx == 0 ? '?' : '&';
            url += ch + 't=' + $(elem).val();
        });
        window.location.href = url;
        return false;
    });

    $('body').on('click', 'input.track-select', function(e) {
        var tr = $(this).parent().parent();
        var btn = $('#track-select');
        $(this).is(':checked') ? tr.addClass('info') : tr.removeClass('info');
        // Update the dropdown and select all checkbox.
        var num_checked = $('input.track-select:checked').length;
        var num_inputs = $('input.track-select').length;
        if(num_checked > 0) {
            btn.removeClass('disabled');
        }
        else {
            btn.addClass('disabled');
        }
        $('input.select-all').prop('checked', num_checked == num_inputs);
    });

    $('body').on('click', 'input.select-all', function(e) {
        var inputs = $('input.track-select');
        var rows = $('tbody.tracks tr');
        var btn = $('#track-select');
        if($(this).is(':checked')) {
            inputs.prop('checked', true);
            rows.addClass('info');
            btn.removeClass('disabled');
        }
        else {
            inputs.prop('checked', false);
            rows.removeClass('info');
            btn.addClass('disabled');
        }
    });

    $('body').on('click', 'a.track-edit', function(e) {
        var track_ids = [];
        $('input.track-select:checked').each(function(idx, elem) {
            track_ids.push($(elem).val());
        });
        $.ajax({
            url: $(this).attr('href'),
            data: {t: track_ids},
            traditional: true,
            dataType: 'html',
            success: function(html) {
                $('#modal').empty().append(html).modal();
            }
        });
        return false;
    });

    $('body').on('click', 'a.track-save', function(e) {
        var form = $('form.track-form');
        console.log(form.serialize());
        $.ajax({
            url: form.attr('action'),
            type: 'POST',
            data: form.serialize(),
            success: function(html) {
                console.log(html);
            }
        });
        return false;
    });

    $('#search-form').submit(function() {
        load_page({q: $('#q').val()});
        return false;
    });

    load_page({q: $('#q').val()});
});
