const host = window.location.protocol + "//" + window.location.host;

window.onload = function () {
    const createGameForm = document.getElementById("add-vessel-form");
    if (createGameForm != null) {
        createGameForm.addEventListener("submit", create_game);
    }

    // load fleet when page is loaded
    const urlParams = new URLSearchParams(window.location.search);
    const gameId = urlParams.get("game-id");
    const playerName = urlParams.get("player-name");
    document.getElementById("game-id").value = gameId;
    document.getElementById("player-name").value = playerName;
    updateVesselTable(gameId, playerName).then(function () {
        console.log("Vessels table updated!")
    });

    // load fleet if load-fleet button is clicked
    const loadFleetButton = document.getElementById("load-fleet");
    if (loadFleetButton != null) {
        loadFleetButton.addEventListener("click", updateVessel);
    }

    // Click Play button
    const playButton = document.getElementById("play-game");
    if (playButton != null) {
        playButton.addEventListener("click", playGame);
    }
};

function playGame() {
    const playerName = document.getElementById("player-name").value;
    const gameId = document.getElementById("game-id").value;
    window.location.href = "play_game.html?game-id=" + gameId  + "&player-name=" + playerName;
}

function updateVessel() {
    updateVesselTable(document.getElementById("game-id").value,
        document.getElementById("player-name").value)
        .then(function () {
            console.log("Vessels table updated!")
        })
}

async function create_game(event) {
    event.preventDefault();
    console.log("start request")
    const form = event.currentTarget;
    const formData = new FormData(form);
    const plainFormData = Object.fromEntries(formData.entries());
    const formDataJsonString = JSON.stringify(plainFormData);
    const response = await postData(host + "/add-vessel", formDataJsonString)
    let resultAddVessel = document.getElementById("add-vessel-result");
    resultAddVessel.innerHTML = '';
    let h1 = document.createElement('H1');
    resultAddVessel.appendChild(h1)
    if (!response.ok) {
        const error = await response.json();
        console.log(error)
        h1.innerHTML = "Erreur: " + error.message;
        h1.className = "error";
    } else {
        h1.innerHTML = "Vaisseau créé avec succès";
        h1.className = "success";
        await updateVesselTable(formData.get("game_id"), formData.get("player_name"));
    }
    resultAddVessel.style.visibility = "visible";
}

async function postData(url = '', data) {
    const fetchOptions = {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "Accept": "application/json"
        },
        body: data,
    };
    return fetch(url, fetchOptions);
}

async function getData(url = '') {
    const fetchOptions = {
        method: "GET",
        headers: {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
    };
    return fetch(url, fetchOptions);
}

async function updateVesselTable(gameId, playerName) {
    const player = await getPlayer(gameId, playerName)
    const vessels = player.battle_field.vessels;
    let table = document.getElementById("vessels-table");
    let old_tbody = table.getElementsByTagName('tbody');
    let new_tbody = document.createElement('tbody');
    vessels.forEach(function (vessel) {
        let tr = document.createElement('tr');
        tr.innerHTML = '<td id=' + vessel.id + '>' + vessel.type + '</td>' +
            '<td>' + vessel.coordinates + '</td>' +
            '<td>' + vessel.hits_to_be_destroyed + '</td>' +
            '<td>' + vessel.weapon.type + '</td>' +
            '<td>' + vessel.weapon.ammunitions + '</td>' +
            '<td>' + vessel.weapon.range + '</td>'
        new_tbody.appendChild(tr);
    });
    table.removeChild(old_tbody[0])
    table.appendChild(new_tbody)
}

async function getPlayer(gameId, playerName) {
    const resource_url = host + "/get-player?game_id=" + gameId + "&player_name=" + playerName;
    const response = await getData(resource_url);
    if (!response.ok) {
        return {player_name: playerName, battle_field: {vessels: []}};
    } else {
        return response.json();
    }
}