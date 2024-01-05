const host = window.location.protocol + "//" + window.location.host;
const url = host + "/join-game";

async function join_game(event) {
    event.preventDefault();
    console.log("start request")
    const form = event.currentTarget;
    const formData = new FormData(form);
    const plainFormData = Object.fromEntries(formData.entries());
    const formDataJsonString = JSON.stringify(plainFormData);
    const response = await postData(url, formDataJsonString);
    const joinGameForm = document.getElementById("join-game-form");
    const resultJointGame = document.getElementById("join-game-result");
    const h1 = document.createElement('H1');
    resultJointGame.appendChild(h1)
    if (!response.ok) {
        const error = await response.json();
        console.log(error)
        h1.innerHTML = "Erreur: " + error.message;
        h1.className = "error";
    } else {
        h1.innerHTML = "Vous avez rejoint la partie avec succés !<br>";
        let linkToVessels = document.createElement("a");
        const playerName = document.getElementById("player-name").value;
        const gameId = document.getElementById("game-id").value;
        linkToVessels.href = "manage_fleet.html?game-id=" + gameId + "&player-name=" + playerName;
        linkToVessels.text = "Gérer votre flotte !"
        h1.appendChild(linkToVessels);
        h1.className = "success";
    }
    joinGameForm.style.visibility = "hidden";
    resultJointGame.style.visibility = "visible";


}

window.onload = function () {
    const joinGameForm = document.getElementById("join-game-form");
    if (joinGameForm != null) {
        joinGameForm.addEventListener("submit", join_game);
    }
};

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
