$(function() {
    $('#search').typeahead({
        minLength: 2,
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
            return item.html;
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
});
