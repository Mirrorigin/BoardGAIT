let playerName;

// Initialize fullPage.js
new fullpage('#fullpage', {
    licenseKey: '',
    autoScrolling: true,
    navigation: true,
    onLeave: (origin, destination, direction) => {
        // Prevents access to the second screen if the player name is not entered
        if (destination.index === 1 && !playerName) {
            showFlashMessage('Please enter your name before proceeding.', "error");
            return false;
        }
    }
});

function showFlashMessage(message, type = "success") {
    const flash = document.getElementById('flash-message');
    flash.textContent = message;

    flash.classList.remove('success', 'error');
    flash.classList.add(type);
    flash.classList.add('show');

    setTimeout(() => {
        flash.classList.remove('show');
    }, 3000);
}

// Invite player to join game
async function joinGame() {
    const inputField = document.getElementById('player-name');
    const errorMessage = document.getElementById('error-message');

    playerName = inputField.value.trim();
    if (!playerName) {
        errorMessage.textContent = "Please enter a valid name.";
        return;
    }

    errorMessage.textContent = "";  // Clear previous error messages
    fullpage_api.moveSectionDown(); // Slide to the next page
    fullpage_api.setAllowScrolling(false, 'up');    // No scrolling up

    showFlashMessage("Success! You have joined the game.", "success");

    const loadingIndicator = document.getElementById('loading-indicator');
    loadingIndicator.style.display = "block";   // Display loading animation...

    // Send a request to join the game and initialize the game
    try {
        const response = await fetch('/join_game', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ player: playerName })
        });

        const data = await response.json();
        const startGameButton = document.getElementById('start-game-button');

        // Wait for the server to respond...
        if (response.ok) {
            console.log("Game initialized successfully!");
            console.log("Agents:", data.agents);
            displayAgents(data.agents);
            startGameButton.disabled = false;   // Enable the Start_Game button
            startGameButton.classList.add('enabled');
        } else {
            errorMessage.textContent = data.error;
            fullpage_api.moveSectionUp();
        }
    } catch (error) {
        console.error("Error during join game:", error);
        errorMessage.textContent = "An error occurred. Please try again.";
        fullpage_api.moveSectionUp();
    } finally {
        loadingIndicator.style.display = "none";
    }
}

function displayAgents(agents) {
    const container = document.getElementById('agent-display');
    container.innerHTML = "";   // Empty the container

    let index = 0;

    function showEachAgent() {
        if (index >= agents.length) return; // All agents are displayed successfully

        const agentName = agents[index];

        // Create the Agent avatar and name elements
        const agentElement = document.createElement('div');
        agentElement.style.textAlign = "center";

        const avatar = document.createElement('img');
        avatar.src = "https://via.placeholder.com/150"; // mock
        avatar.alt = agentName;
        avatar.style.width = "150px";
        avatar.style.height = "150px";
        avatar.style.borderRadius = "50%";

        const name = document.createElement('p');
        name.textContent = agentName;
        name.style.fontSize = "20px";

        // Add the avatar and name to the container
        agentElement.appendChild(avatar);
        agentElement.appendChild(name);

        // Add containers to the display area
        container.appendChild(agentElement);

        index++;
        setTimeout(showEachAgent, 1000);
    }
    showEachAgent();
}

async function startGame() {
    window.location.href = '/game';
}