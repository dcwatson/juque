$(function() {
    $('#q').focus().select();

    $('a.play').click(function() {
        var url = $(this).data('track-url');
        var player = document.getElementById('player');
        $(player).attr('src', url);
        player.play();
        return false;
    });
});
