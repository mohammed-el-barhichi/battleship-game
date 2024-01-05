const host = window.location.protocol + "//" + window.location.host;

window.onload = function () {
    // load game
    const urlParams = new URLSearchParams(window.location.search);
    const gameId = urlParams.get("game-id");
    const playerName = urlParams.get("player-name");
    updateVesselTable(gameId, playerName)
        .then(function () {
            console.log("Your vessels updated !")
        });

    // handle fire submit form
    const fireForm = document.getElementById("fire-form");
    if (fireForm != null) {
        fireForm.addEventListener("submit", fire);
    }
}

async function fire(event) {
    event.preventDefault();
    console.log("start fire")
    const urlParams = new URLSearchParams(window.location.search);
    const form = event.currentTarget;
    const formData = new FormData(form);
    let plainFormData = Object.fromEntries(formData.entries());
    const gameId = urlParams.get("game-id");
    const playerName = urlParams.get("player-name");
    plainFormData['game_id'] = gameId;
    plainFormData['shooter_name'] = playerName;
    const formDataJsonString = JSON.stringify(plainFormData);
    const response = await postData(host + "/shoot-at", formDataJsonString);
    const resultFire = document.getElementById("fire-result");
    resultFire.innerHTML = "";
    let h1 = document.createElement('H1');
    resultFire.appendChild(h1)
    if (!response.ok) {
        const error = await response.json();
        console.log(error)
        h1.innerHTML = "Raté! " + error.message;
        h1.className = "error";
    } else {
        const result = await response.json();
        console.log(result)
        h1.innerText = result ? "Touché!" : "Raté!"
        h1.className = result ? "success" : "error";
    }
    resultFire.style.visibility = "visible";
    updateVesselTable(gameId, playerName)
        .then(function () {
            console.log("Your vessels updated !")
        });

    const resultGameStatus = document.getElementById("game-result");
    resultGameStatus.innerHTML = "";
    let status_h1 = document.createElement('H1');
    resultGameStatus.appendChild(status_h1)
    const resource_url = host + "/game-status?game_id=" + gameId + "&player_name=" + playerName;
    const game_status_response = await getData(resource_url);
    if (!game_status_response.ok) {
        const error = await game_status_response.text();
        console.log(error)
        status_h1.innerHTML = error.message;
        status_h1.className = "error";
    } else {
        const resp = await game_status_response.json();
        if(resp === 'GAGNE') {
            status_h1.className = "success";
            status_h1.innerHTML = "Félicitations! Vous avez gagné la partie !";
        }
        if(resp === 'PERDU') {
            status_h1.className = "error";
            status_h1.innerHTML = "Dommage! Vous avez perdu!";
        }

    }
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

async function postData(url = '', data) {
    console.log("post data to " + url)
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

async function updateVesselTable(gameId, playerName) {
    const player = await getPlayer(gameId, playerName)
    createBattleField(player.battle_field);
    const vessels = player.battle_field.vessels;
    let table = document.getElementById("your-table");
    let old_tbody = table.getElementsByTagName('tbody');
    let new_tbody = document.createElement('tbody');
    vessels.forEach(function (vessel) {
        let tr = document.createElement('tr');
        tr.setAttribute("id", vessel.id);
        tr.setAttribute("onclick", "selectVessel(" + vessel.id + ", " + vessel.coordinates + ")");
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

function selectVessel(elementId, x, y, z) {
    const table = document.getElementById("your-table");
    const rows = table.getElementsByTagName("tr");
    for (let i = 0; i < rows.length; i++) {
        const tr = rows[i];
        tr.classList.remove("selected");
    }
    const row = document.getElementById(elementId);
    row.className = "selected";
    const vesselIdElement = document.getElementById("vessel-id");
    vesselIdElement.value = elementId;
    showMyVesselInBattleField(x, y, z);
}

function showMyVesselInBattleField(x, y, z) {
    const table = document.getElementById("battle-field");
    const cells = table.getElementsByTagName("td");
    for (let i = 0; i < cells.length; i++) {
        const td = cells[i];
        td.classList.remove("friend-vessel");
    }
    const td = document.getElementById(x + "," + y);
    td.className = "friend-vessel";
}

function createBattleField(battlefield) {
    let table = document.getElementById("battle-field");
    table.innerHTML = "";
    let dimensionX = battlefield.max_x - battlefield.min_x;
    let dimensionY = battlefield.max_y - battlefield.min_y;
    for (let y = 0; y < dimensionY; y++) {
        let tr = document.createElement('tr');
        table.appendChild(tr);
        for (let x = 0; x < dimensionX; x++) {
            let td = document.createElement('td');
            let coord = x + "," + y;
            td.setAttribute("onclick", "selectTargetVessel(" + x + ", " + y + ")");
            td.setAttribute("id", coord)
            tr.appendChild(td);
        }

    }
}

function selectTargetVessel(x, y) {
    const table = document.getElementById("battle-field");
    const cells = table.getElementsByTagName("td");
    for (let i = 0; i < cells.length; i++) {
        const td = cells[i];
        td.classList.remove("target-vessel");
    }
    const td = document.getElementById(x + "," + y);
    td.className = "target-vessel";
    const coord_x = document.getElementById("x");
    coord_x.value = x;
    const coord_y = document.getElementById("y");
    coord_y.value = y;
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