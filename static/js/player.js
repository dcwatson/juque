$(function() {
    setTimeout( function() {
        window.scrollTo(0, 1);
    }, 0);

    var player = document.getElementById('player');
    var playing = false;

    $('#play').click(function() {
        if(!playing) {
            $('i', this).removeClass('icon-play').addClass('icon-pause');
            player.play();
            playing = true;
        }
        else {
            $('i', this).removeClass('icon-pause').addClass('icon-play');
            player.pause();
            playing = false;
        }
        return false;
    });
});
