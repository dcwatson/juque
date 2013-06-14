$(function() {
    var cls = 'li.nav-' + $('body').attr('class');
    $(cls).addClass('active');

    $('select').chosen();

    if(initial_field) {
        $('#' + initial_field).focus().select();
    }

    $('#q').typeahead({
        minLength: 2,
        items: 8,
        source: function(query, process) {
            $.ajax({
                url: query_url,
                data: {q: query},
                dataType: 'json',
                success: function(data) {
                    data.unshift({
                        type: 'query',
                        query: query,
                        html: '<span class="query"><i class="icon-search"></i> ' + query + '</span>'
                    });
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
                    var now = obj.artist + ' ' + String.fromCharCode(8212) + ' ' + obj.name;
                    $('#artwork').attr('src', obj.artwork_url);
                    $('#now-playing').text(now);

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
            return item.html;
        }
    });
});
