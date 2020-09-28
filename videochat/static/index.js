let btn = document.getElementById('btn-new-room');
let loader = document.getElementById('btn-loader');
let roomForm = document.getElementById('room-form');
let roomLink = document.getElementById('room-link');

btn.onclick = () => {
    var xhr = new XMLHttpRequest();
    xhr.open(
        'POST',
        window._config['api_url'],
        true
    );
    xhr.onload = function () {
        loader.style.display = "none";
        roomForm.style.display = "";
        let link = JSON.parse(xhr.response)['room_link'];
        roomLink.value = link;
        roomForm.action = link;
    };
    xhr.send()
    btn.style.display = "none";
    loader.style.display = "inline";
};