$(function() {
    var cls = 'li.nav-' + $('body').attr('class');
    $(cls).addClass('active');

    $('select').chosen();

    if(initial_field) {
        $('#' + initial_field).focus().select();
    }

    $('#q').typeahead({
        minLength: 3,
        items: 8,
        source: function(query, process) {
            $.ajax({
                url: query_url,
                data: {q: query},
                dataType: 'json',
                success: function(data) {
                    data.unshift({type: 'query', query: query});
                    // A dirty hack to make sure our updater method gets an object instead of the string "[Object]"
                    $.each(data, function(idx, item) {
                        item.toString = function() { return JSON.stringify(item); };
                    });
                    process(data);
                }
            });
        },
        matcher: function(item) {
            return true;
        },
        sorter: function(items) {
            return items;
        },
        updater: function(item) {
            obj = JSON.parse(item);
            if(obj.type == 'track') {
                var player = document.getElementById('player');
                if(player) {
                    $('div.artwork img').attr('src', obj.artwork_url);
                    $('div.artwork .track').text(obj.name);
                    $('div.artwork .artist').text(obj.artist);
                    $(player).attr('src', obj.url);
                    player.play();
                    $.ajax({
                        url: '/library/ajax/play/' + obj.id + '/'
                    });
                }
            }
            else if(obj.type == 'artist') {
                window.location.href = obj.url;
                return obj.name;
            }
            else if(obj.type == 'query') {
                $('#q').val(obj.query);
                $('#search-form').submit();
                return obj.query;
            }
            return '';
        },
        highlighter: function(item) {
            var html = '';
            if(item.type == 'track') {
                var line = [];
                html += '<span class="query-track">' + item.name + '</span>';
                if(item.artist) {
                    line.push(item.artist);
                }
                if(item.album) {
                    line.push(item.album);
                }
                if(line) {
                    html += '<span class="query-track-artist">' + line.join(' &mdash; ') + '</span>';
                }
            }
            else if(item.type == 'artist') {
                html += '<span class="query-artist"><i class="icon-user"></i> ' + item.name + '</span>';
            }
            else if(item.type == 'query') {
                html += '<span class="query"><i class="icon-search"></i> ' + item.query + '</span>';
            }
            return html;
        }
    });
});
