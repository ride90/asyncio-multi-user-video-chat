window.URL = window.URL || window.webkitURL;
window.MediaSource = window.MediaSource || window.WebKitMediaSource;
if (!!!window.MediaSource) {
    alert('MediaSource API is not available. Try another browser.');
}
const roomID = window.location.pathname.split('/')[2]
let roomJoined = false;
let ws = null;
const videoClient = document.getElementById('video-client');
const videoServer = document.getElementById('video-server');
const codec = 'video/webm; codecs="vp8"';
let mediaSource = new window.MediaSource();
let mediaSourceBuffer = null;


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
        console.log('onmessage', typeof e.data);

        if (typeof e.data === "string") {
            let data = JSON.parse(e.data);
            if (data['status'] === 'joined') {
                roomJoined = true;
            }
        } else if (mediaSourceBuffer != null && !mediaSourceBuffer.updating) {
            // add bytes to buffer
            console.log(e);
            mediaSourceBuffer.appendBuffer(
                new Uint8Array(e.data)
                //e.data
            );
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

        // this is how we get media
        const recorder = new MediaRecorder(stream, {mimeType: codec});
        recorder.ondataavailable = event => {
            if (roomJoined && ws.readyState === 1) {
                const blob = new Blob([event.data], {'type': codec});
                console.log("SEND BLOB")
                ws.send(blob);
            }
        };
        recorder.start(1000);
    })

videoServer.src = window.URL.createObjectURL(mediaSource);
mediaSource.addEventListener('sourceopen', function (e) {
    console.log('MediaSource sourceopen')
    // buffer for video media source
    mediaSourceBuffer = mediaSource.addSourceBuffer(codec);
});

// connect to ws
connectWebSocket();
