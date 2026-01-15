function addOrUpdateQueryParam(key, value) {
    const currentUrl = new URL(window.location.href);

    currentUrl.searchParams.set(key, value);

    if (!value) {
        currentUrl.searchParams.delete(key);
    }

    window.history.pushState(null, '', currentUrl.toString());
}

function genQRCode(url) {
    const qrimg = document.getElementById('qrimg');

    QRCode.toDataURL(url).then((dataUrl) => {
      qrimg.src = dataUrl;
      qrimg.style.visibility = '';

      const spanElement = document.getElementById("room-link");
      spanElement.textContent = url;
    })
}

function copyLinkToTransfer() {
    const link = window.location.toString();
    navigator.clipboard.writeText(link)
        .then(() => {
            const copyLinkButton = document.getElementById('copy-link-btn');
            const currentText = copyLinkButton.innerText;
            copyLinkButton.disabled = true;
            copyLinkButton.innerText = 'Link copiado! 🔗🔗';

            setTimeout(()=> {
                copyLinkButton.disabled = false;
                copyLinkButton.innerText = currentText;
            }, 5000)
        })
        .catch(err => {
          console.error('Falha ao copiar o texto: ', err);
        });
}

document.addEventListener("DOMContentLoaded", () => {
    const socket = io({closeOnBeforeunload: true});

    // Connection handlers
    socket.on('connect', () => {
        console.log('Client has been connected successfully!');
        socket.emit('connected');
    });
    socket.on('connect_response', (msg) => {
        const youPlayerEl = document.getElementById("you-player");
        youPlayerEl.textContent = msg.username;

        // Start game
        const currentUrl = new URL(window.location.href);
        const roomId = currentUrl.searchParams.get('room') || '';
        socket.emit('start_game', {roomId});
    });
    socket.on('start_game_response', function(msg) {
        const roomId = msg.roomId;
        const error = msg.error;

        if (roomId && !error) {
            addOrUpdateQueryParam('room', msg.roomId);
            genQRCode(window.location.toString())

            const copyLinkBtn = document.getElementById('copy-link-btn');
            copyLinkBtn.addEventListener('click', ()=> {
                copyLinkToTransfer();
            });
        }

        if (error) {
            const errors  = {
              full: `A sala atual está <b>Cheia</b>, crie uma sala nova ⚙️⚙️🚀!`,
              invalid: `A é  <b>inválida</b>, crie uma sala nova  ⚙️⚙️🚀!`,
            };
            const bannerAlert = document.getElementById('banner-alert');
            bannerAlert.innerHTML = errors[error];
            bannerAlert.classList.add('show');
        }
    });
    socket.on('game_ready', (msg) => {
        const gameReady = msg.ready;

        if (!gameReady) {
            const youPickEl = document.getElementById('you-pick');
            youPickEl.innerText = 'Esperando Oponente ... ⏳';

            const radioGroups = document.querySelectorAll('#you-container .image-radio-group');
            for (const radioGroup of radioGroups) {
                radioGroup.classList.add('not-clickable-div');
            }

            const radioInputs = document.querySelectorAll('#you-container .image-radio-group input[type="radio"]');
            radioInputs.forEach(r => r.checked = false);

            const spanElement = document.getElementById("you-username");
            spanElement.textContent = 'Esperando Oponente... ⏳';

            const theyUsername = document.getElementById('they-username');
            theyUsername.innerText = 'Esperando Oponente ... ⏳';

            const theyActions = document.getElementById("they-actions");
            theyActions.style.display = 'none';
            const theyJoin = document.getElementById("they-join");
            theyJoin.style.display = 'block';
            return false;
        }

        const isPLaying = Boolean(document.getElementById('is-playing').innerText);

        if (!isPLaying) {
            const radioGroup = document.querySelector('#you-container .image-radio-group');
            radioGroup.classList.remove('not-clickable-div');

            const youPickEl = document.getElementById('you-pick');
            youPickEl.innerText = 'Escolha o Seu 🤔';
        }

        const youPlayerEl = document.getElementById("you-player");
        const youUsername = document.getElementById("you-username");
        const theyUsername = document.getElementById('they-username');

        if (isPLaying) {
            const playAgain = document.getElementById('banner-play-again');

            if (msg.match?.result === 'tie') {
                playAgain.innerHTML = `<button onclick="window.location.reload()" class="flash-button">Empate 😑, Jogue Novamente!</button>`;
                confetti({
                  shapes: [confetti.shapeFromText({ text: '😑', scalar: 10 })],
                });
            } else if (msg.match?.result === 'won') {
                if (youPlayerEl.textContent === msg.match?.username) {
                    playAgain.innerHTML = `<button onclick="window.location.reload()" class="flash-button">Você ganhou 🏆, Jogue Novamente!</button>`;
                    confetti({
                      particleCount: 100,
                      spread: 70,
                      origin: { y: 0.6 }
                    });
                } else {
                    playAgain.innerHTML = `<button onclick="window.location.reload()" class="flash-button">Você Perdeu 🪦, Jogue Novamente!</button>`;
                    confetti({
                      shapes: [confetti.shapeFromText({ text: '🪦', scalar: 10 })],
                    });
                }
            }
        }

        youUsername.textContent = (youPlayerEl.textContent === msg.player1) ? msg.player1: msg.player2;
        theyUsername.innerText = (youPlayerEl.textContent === msg.player1) ? msg.player2: msg.player1;

        const theyActions = document.getElementById("they-actions");
        theyActions.style.display = 'block';
        const theyJoin = document.getElementById("they-join");
        theyJoin.style.display = 'none';
    });

    document.querySelectorAll('#you-container .image-radio-group input[name="you-choice"]').forEach(radio => {
        radio.addEventListener('change', (event) => {
            const youPickEl = document.getElementById('you-pick');
            youPickEl.innerText = 'Você Escolheu 🎉';

            const currentUrl = new URL(window.location.href);
            const roomId = currentUrl.searchParams.get('room');
            const action = event.target.value;
            socket.emit('play_action', {action, roomId});

            const isPLaying = document.getElementById('is-playing');
            isPLaying.innerText = 'true';

            const radioGroup = document.querySelector('#you-container .image-radio-group');
            radioGroup.classList.add('not-clickable-div');
        });
    });
    socket.on('play_action_response', (msg) => {
        const youPlayerEl = document.getElementById("you-player");
        if (youPlayerEl.textContent === msg.username) {
            const radioInput = document.querySelector(`.they-picked-fake-class`);

            if (radioInput) {
                radioInput.checked = true;
            }
        }
        if (youPlayerEl.textContent !== msg.username) {
            const isPLaying = Boolean(document.getElementById('is-playing').innerText);

            const radioInput = document.querySelector(`#they-actions .image-radio-group #they-${msg.action}`);
            if (isPLaying) {
                radioInput.checked = true;
            } else {
                radioInput.classList.add('they-picked-fake-class');
            }

            const youPickEl = document.getElementById('they-pick');
            youPickEl.innerText = 'Seu Oponente Escolheu 🎉';
        }
    });
});