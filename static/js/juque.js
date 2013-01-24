$(function() {
    $('#q').focus().select();

    $('a.play').click(function() {
        var url = $(this).data('track-url');
        $('div.player img').attr('src', $(this).data('cover-url'));
        $('div.player .track').text($(this).data('title'));
        $('div.player .artist').text($(this).data('artist'));
        var player = document.getElementById('player');
        $(player).attr('src', url);
        player.play();
        return false;
    });

    $('select').chosen();
});
