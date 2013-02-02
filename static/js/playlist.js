$(function() {
    $('#search').typeahead({
        minLength: 3,
        items: 8,
        source: function(query, process) {
            $.ajax({
                url: track_url,
                data: {q: query, n: 8},
                dataType: 'json',
                success: function(data) {
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
            var obj = JSON.parse(item);
            var row = '<tr>';
            row += '<td><i class="icon-reorder handle"></i></td>';
            row += '<td>' + obj.track + '<input type="hidden" name="tracks" value="' + obj.pk + '" /></td>';
            row += '<td>' + obj.artist + '</td>';
            row += '<td class="right">' + obj.length + '</td>';
            row += '<td class="right"><a class="btn btn-mini delete"><i class="icon-remove"></i></a></td>';
            row += '</tr>';
            $('#tracks').append(row);
            return '';
        },
        highlighter: function(item) {
            var html = '<span class="track">' + item.track + '</span>';
            var line = [];
            if(item.artist) {
                line.push(item.artist);
            }
            if(item.album) {
                line.push(item.album);
            }
            if(line) {
                html += '<span class="artist">' + line.join(' &mdash; ') + '</span>';
            }
            return html;
        }
    });
    $('#tracks').sortable({
        axis: 'y',
        cursor: 'move',
        handle: '.handle'
    });
    $('body').on('click', 'a.delete', function(e) {
        var row = $(this).parent().parent();
        row.remove();
    });
    $('#search').focus().select();
});
