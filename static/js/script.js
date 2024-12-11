let playerName;

// Initialize fullPage.js
new fullpage('#fullpage', {
    licenseKey: '',
    autoScrolling: true,
    navigation: true,
    onLeave: (origin, destination, direction) => {

        const agentDisplay = document.getElementById('agent-display-container');
        const startGameButton = document.getElementById('start-game-button');

        // Control agent-display visible or hidden
        if (destination.index === 1 || destination.index === 2) {
            agentDisplay.style.display = 'block';
            console.log('Agent Display Container Style:', agentDisplay.style.display);
        } else {
            agentDisplay.style.display = 'none';
        }

        // Control  Start_Game visible or hidden
        if (destination.index === 1) {
            startGameButton.style.display = 'block';
        } else {
            startGameButton.style.display = 'none';
        }

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
    fullpage_api.setAllowScrolling(false, 'down');  // No scrolling down

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
            console.log("Agents:", data.agent_names, data.agent_infos, data.agent_avatars);
            displayAgents(data.agent_names, data.agent_infos, data.agent_avatars);
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

function displayAgents(agent_names, agent_infos, agent_avatars) {
    const container = document.getElementById('agent-display');
    container.innerHTML = "";   // Empty the container

    let index = 0;

    function showEachAgent() {
        if (index >= agent_names.length) return; // All agents are displayed successfully

        const agentName = agent_names[index];
        const agentInfo = agent_infos[index];
        const agentAvatar = agent_avatars[index];
        const tooltip = document.getElementById('tooltip');
        // Create the Agent avatar and name elements
        const agentElement = document.createElement('div');

        agentElement.setAttribute('data-info', agentInfo);

        const avatar = document.createElement('img');
        avatar.src = agentAvatar
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

        // Add hover event to show tooltip
        avatar.addEventListener('mouseenter', (event) => {
            console.log('Mouse entered the avatar!');
            tooltip.style.visibility = 'visible';
            tooltip.style.opacity = '1';
            tooltip.textContent = agentInfo;
        });

        avatar.addEventListener('mousemove', (event) => {
            const offsetY = 100;
            const offsetX = 0;
            tooltip.style.top = `${event.clientY - offsetY - tooltip.offsetHeight}px`;
            tooltip.style.left = `${event.clientX + offsetX - tooltip.offsetWidth / 2}px`;
        });

        avatar.addEventListener('mouseleave', () => {
            tooltip.style.visibility = 'hidden';
            tooltip.style.opacity = '0';
        });

        // Add containers to the display area
        container.appendChild(agentElement);

        index++;
        setTimeout(showEachAgent, 1000);
    }
    showEachAgent();
}

async function startGame() {
    try {
        const response = await fetch('/start_game', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
        });

        const data = await response.json();
        if (response.ok) {
            console.log("Game started...");
            console.log("Player Info:", data.player_info);

            // Get current player's identity
            const playerInfo = data.player_info[playerName];
            if (playerInfo) {
                document.getElementById('role-display').textContent = playerInfo.role;
                document.getElementById('word-display').textContent = playerInfo.word;
            } else {
                console.error("Player information not found!");
            }

            // Move to the next section
            fullpage_api.moveSectionDown();
        } else {
            console.error(data.error);
            showFlashMessage(data.error, "error");
        }
    } catch (error) {
        console.error("Error during start game:", error);
        showFlashMessage("An error occurred. Please try again.", "error");
    }
}
