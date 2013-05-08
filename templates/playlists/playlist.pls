[playlist]
NumberOfEntries={{ playlist.get_tracks|length }}
Version=2

{% for t in playlist.get_tracks %}
File{{ forloop.counter }}={{ t.url }}
Title{{ forloop.counter }}={{ t.artist }} - {{ t }}
Length{{ forloop.counter }}={{ t.length|floatformat:0 }}
{% endfor %}
