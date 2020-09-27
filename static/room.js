window.URL = window.URL || window.webkitURL;
window.MediaSource = window.MediaSource || window.WebKitMediaSource;
if (!!!window.MediaSource) {
    alert('MediaSource API is not available. Try another browser.');
}
const roomID = window.location.pathname.split('/')[2]
let roomJoined = false;
let ws = null;
const videoClient = document.getElementById('video-client');
const canvasClient = document.getElementById('canvas-client');
canvasClient.width = 640;
canvasClient.height = 480;
const imgServer = document.getElementById('image-server');

// const codec = 'video/webm; codecs="vp8"';
// let mediaSource = new window.MediaSource();
// let mediaSourceBuffer = null;

function dataURItoBlob(dataURI) {
    // convert base64/URLEncoded data component to raw binary data held in a string
    var byteString;
    if (dataURI.split(',')[0].indexOf('base64') >= 0)
        byteString = atob(dataURI.split(',')[1]);
    else
        byteString = unescape(dataURI.split(',')[1]);

    // separate out the mime component
    var mimeString = dataURI.split(',')[0].split(':')[1].split(';')[0];

    // write the bytes of the string to a typed array
    var ia = new Uint8Array(byteString.length);
    for (var i = 0; i < byteString.length; i++) {
        ia[i] = byteString.charCodeAt(i);
    }

    return new Blob([ia], {type: mimeString});
}

function connectWebSocket() {
    ws = new WebSocket(window._config['ws_url']);
    ws.binaryType = 'arraybuffer';
    ws.onopen = function () {
        console.log("Openened connection to websocket");

        // join room
        ws.send(JSON.stringify({
            'room_id': roomID,
            'action': 'join'
        }));
    }
    ws.onmessage = function (e) {
        console.log('[WS] onmessage', typeof e.data);

        if (typeof e.data === "string") {
            let data = JSON.parse(e.data);
            if (data['status'] === 'joined') {
                console.log('[WS] room joined');
                roomJoined = true;
            }
        } else {
            let url = window.URL.createObjectURL(
                new Blob([e.data], {type: "image/jpeg"})
            )
            imgServer.onload = function () {
                window.URL.revokeObjectURL(url);
            };
            imgServer.src = url;
        }
    };
    ws.onclose = function (e) {
        console.log('Socket is closed. Reconnect will be attempted in 1 second.', e.reason);
        roomJoined = false;
        setTimeout(function () {
            connectWebSocket();
        }, 5000);

    };
    ws.onerror = function (err) {
        console.error('Socket encountered error: ', err.message, 'Closing socket');
        ws.close();
        roomJoined = false;
    };
}

navigator.mediaDevices
    .getUserMedia({
        audio: false,
        video: {
            width: 640,
            height: 480,
            // fuck firefox
            // frameRate: {
            //     ideal: 10,
            //     max: 10
            // }
        }
    })
    .then((stream) => {
        window.stream = stream;
        videoClient.srcObject = stream;
    })

// update canvas every X ms
setInterval(
    function () {
        canvasClient
            .getContext('2d')
            .drawImage(videoClient, 0, 0, canvasClient.width, canvasClient.height);

        // when WS is connected  send canvas as image to the server
        console.log('WS STATE', ws.readyState);
        if (ws.readyState === WebSocket.OPEN && roomJoined) {
            console.log('WS STATE send', ws.readyState);
            let data = canvasClient.toDataURL('image/jpeg', 1.0);
            //
            let blob = dataURItoBlob(data);
            ws.send(blob)
        }
    }, 100
);

// connect to ws
connectWebSocket();
