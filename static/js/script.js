let playerName;

// Initialize fullPage.js
new fullpage('#fullpage', {
    licenseKey: '',
    autoScrolling: true,
    navigation: true,
    onLeave: (origin, destination, direction) => {

        const agentDisplay = document.getElementById('agent-display-container');
        const startGameButton = document.getElementById('start-game-button');
        const descriptionContainer = document.querySelector('.description-input-container');

        // Control agent-display visible or hidden
        if (destination.anchor === "agent-display-page" || destination.anchor === "description-page") {
            agentDisplay.style.display = 'block';
            console.log('Agent Display Container Style:', agentDisplay.style.display);
        } else {
            agentDisplay.style.display = 'none';
        }

        // Control Start_Game visible or hidden
        if (destination.anchor === "agent-display-page") {
            startGameButton.style.display = 'block';
        } else {
            startGameButton.style.display = 'none';
        }

        // Control description-input-container visible or hidden
        if (destination.anchor === "description-page") {
            descriptionContainer.style.display = 'flex';
        } else {
            descriptionContainer.style.display = 'none';
        }

        // Prevents access to the second screen if the player name is not entered
        if ((destination.anchor ==="agent-display-page" && !playerName)) {
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
            displayAgents(data.agent_names, data.agent_infos, data.agent_avatars,() => {
                console.log("All agents displayed. Enabling Start Game button...");
                startGameButton.disabled = false;
                startGameButton.classList.add('enabled');
            });
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

function displayAgents(agent_names, agent_infos, agent_avatars, onComplete) {
    const container = document.getElementById('agent-display');
    container.innerHTML = "";   // Empty the container

    let index = 0;

    function showEachAgent() {
        if (index >= agent_names.length){
            if (typeof onComplete === 'function') {
                onComplete(); // All agents are displayed successfully, callback
            }
            return;
        }

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
        avatar.id = `avatar-${agentName}`; // Add unique ID
        avatar.style.width = "150px";
        avatar.style.height = "150px";
        avatar.style.borderRadius = "50%";

        const nameButton = document.createElement('button');
        nameButton.textContent = agentName;
        nameButton.id = `agent-${agentName}`;
        nameButton.disabled = true;
        nameButton.classList.add('agent-button');

        // Add the avatar and name to the container
        agentElement.appendChild(avatar);
        agentElement.appendChild(nameButton);

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

        nameButton.onclick = function() {
            vote(agentName); // Voting function when the button is clicked
        };

        // Add containers to the display area
        container.appendChild(agentElement);

        index++;
        setTimeout(showEachAgent, 1000);
    }
    showEachAgent();
}

async function startGame() {
    const startGameButton = document.getElementById('start-game-button');
    startGameButton.disabled = true;
    startGameButton.classList.remove('enabled');
    try {
        const response = await fetch('/start_game', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ player: playerName }) // Pass playerName if needed
        });

        const data = await response.json();
        if (response.ok) {
            console.log("Game started...");
            console.log("Player Info:", data.player_info);

            // Get current player's identity
            const playerInfo = data.player_info[playerName];
            if (playerInfo) {
                document.getElementById('player-word').textContent = playerInfo.word;
                showFlashMessage("Game has started!", "success");
            } else {
                console.error("Player information not found!");
                showFlashMessage("Player information not found.", "error");
                return; // Exit the function if player info is missing
            }

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

async function generateDescription() {
    const generateButton = document.getElementById('generate-description-button');
    const descriptionInput = document.getElementById('description-input');

    // Disable button to prevent repeated requests
    generateButton.disabled = true;
    generateButton.textContent = "Generating...";

    try {
        const response = await fetch('/generate_description', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ player: playerName })
        });

        if (response.ok) {
            const data = await response.json();
            const aiDescription = data.description;

            // Fill the generated description into the input box
            descriptionInput.value = aiDescription;
            showFlashMessage("AI description generated! You can edit it before submitting.", "success");
        } else {
            const error = await response.json();
            showFlashMessage(error.message || "Failed to generate description.", "error");
        }
    } catch (error) {
        console.error("Error generating description:", error);
        showFlashMessage("An error occurred. Please try again.", "error");
    } finally {
        // Re-enable button
        generateButton.disabled = false;
        generateButton.textContent = "AI Assist";
    }
}

// Function to submit the description
async function submitDescription() {

    const description = document.getElementById('description-input').value.trim();
    if (description === "") {
        showFlashMessage("Please enter a description before submitting.", "error");
        return;
    }

    // Process the description as needed
    console.log("Description submitted:", description);

    // Clear the input field after submission
    document.getElementById('description-input').value = "";
    // Disable to input and submit
    document.getElementById('description-input').disabled = true;
    document.getElementById('submit-description-button').disabled = true;

    // Send the description to the server
    try {
        const response = await fetch('/describe', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ player: playerName, description: description })
        });
        const data = await response.json();
        if (response.ok) {
            showFlashMessage("All player provided descriptions!", "success");
            setTimeout(() => {
                removeHighlightCurrentPlayer();
                console.log("Highlights removed after 3 seconds.");
            }, 3000);
        } else {
            showFlashMessage(data.error || "Failed to submit description.", "error");
        }
    } catch (error) {
        console.error("Error during description submission:", error);
        showFlashMessage("An error occurred. Please try again.", "error");
    }
}

// Connect to WebSocket
const socket = io();

// Listen for a connection event
socket.on('connect', () => {
    console.log('Successfully connected to the server');
});

// Listen to 'AI_player_describing'
socket.on('ai_description_generated', function(data) {
    const player = data.player;
    console.log("Socket received the data!")
    // Update page effect: Make the current player avatar larger
    highlightCurrentPlayer(player);
    // Update page effect: Make the current player avatar larger
    addDescriptionToLog(player, data.player_description)
});

// Listen to 'player_describing'
socket.on('player_description_valid', function(data) {
    const player = data.player;
    const player_description = data.player_description;
    console.log("Socket received the data!")
    // Update page effect: Make the current player avatar larger
    addDescriptionToLog(player, player_description)
});

socket.on('all_descriptions_generated', function(data) {
    const activePlayers = data.active_players;
    // Enable the vote buttons now that all descriptions are generated
    console.log("Socket received the data!")
    enableVotingButtons(activePlayers)
});

function highlightCurrentPlayer(player) {
    // Remove highlight from all avatars
    removeHighlightCurrentPlayer()

    // Highlight the current player avatar
    const currentPlayerAvatar = document.querySelector(`#avatar-${player}`);
    if (currentPlayerAvatar) {
        currentPlayerAvatar.classList.add('highlight');
        console.log(`Highlighted player: ${player}`);
    } else {
        console.error(`Player avatar not found: #avatar-${player}`);
    }
    // Highlight the current player name
    const currentPlayerName = document.querySelector(`#agent-${player}`);
    if (currentPlayerName) {
        currentPlayerName.classList.add('highlight');
    }
}

function removeHighlightCurrentPlayer() {
    document.querySelectorAll('#agent-display img').forEach(avatar => {
        // console.log(avatar)
        avatar.classList.remove('highlight');
    });
    document.querySelectorAll('#agent-display .agent-button').forEach(nameButton => {
        nameButton.classList.remove('highlight');
    });
}

function addDescriptionToLog(player, description) {
    const descriptionLogContainer = document.getElementById('description-log-container');
    const descriptionLog = document.getElementById('description-log');
    const logItem = document.createElement('li');

    // Create a span for the player's name and apply color
    const playerSpan = document.createElement('span');
    playerSpan.textContent = `${player}: `;
    playerSpan.style.color = '#E6A8B7'; // You can change this color to whatever you like
    playerSpan.style.fontWeight = 'bold';

    // Create a span for the description and apply color
    const descriptionSpan = document.createElement('span');
    descriptionSpan.textContent = description;
    descriptionSpan.style.color = '#FFFFFF'; // You can change this color to whatever you like

    // Append the player and description spans to the log item
    logItem.appendChild(playerSpan);
    logItem.appendChild(descriptionSpan);

    // Add the log item to the description log
    descriptionLog.appendChild(logItem);

    if (!descriptionLogContainer.classList.contains('visible')) {
        descriptionLogContainer.classList.add('visible');
    }
}

function enableVotingButtons(activePlayers = []) {
    const buttons = document.querySelectorAll('.agent-button');
    console.log(buttons);
    buttons.forEach(button => {
        const playerName = button.textContent;

        // The button is enabled only when the player is in the activePlayers list
        if (activePlayers.includes(playerName)) {
            button.disabled = false;
        } else {
            button.disabled = true;
        }
    });
}

async function vote(target) {
    // Here, you can get the current player and send the vote request
    const voter = playerName;  // Use the global playerName variable
    console.log("You choose:", target)
    showFlashMessage(`You voted for ${target}!`, "success");
    resetResultsPage();
    fullpage_api.moveTo('results-page');

    try {
        const response = await fetch('/vote', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ voter: voter, target: target })
        });

        const data = await response.json();

        if (response.ok) {
            console.log("Vote recorded:", data);

            if (data.game_status === "exit") {
                // player eliminated
                // alert(`${playerName}, you have been eliminated. Refresh the page to exit.`);
                fullpage_api.moveTo('exit-page');
            } else if (data.game_status === "win") {
                 fullpage_api.moveTo('win-page');
            } else {
                updateResultsPage(data.eliminated);
                setTimeout(() => {
                    fullpage_api.moveTo('description-page');

                    resetDescriptionInput();
                    disableVotingButtons();
                    clearPreviousRoundData();
                    grayOutInactiveAgents(data.active_players);
                }, 3000);
            }
        } else {
            console.error("Vote error:", data.error);
            showFlashMessage(data.error || "An error occurred during voting.", "error");
        }
    } catch (error) {
        console.error("Error during voting:", error);
        showFlashMessage("An error occurred. Please try again.", "error");
    }
}

function resetResultsPage() {
    const roundSummary = document.getElementById('round-summary');
    roundSummary.innerHTML = "";
}

function updateResultsPage(eliminatedPlayer) {
    const roundSummary = document.getElementById('round-summary');
    const eliminatedItem = document.createElement('li');
    eliminatedItem.textContent = `${eliminatedPlayer} was eliminated.`;
    roundSummary.appendChild(eliminatedItem);

    const statusItem = document.createElement('li');
    statusItem.textContent = "The undercover remains hidden!";
    roundSummary.appendChild(statusItem);
}


function resetDescriptionInput() {
    const descriptionInput = document.getElementById('description-input');
    const submitButton = document.getElementById('submit-description-button');

    if (descriptionInput && submitButton) {

        descriptionInput.value = "";

        descriptionInput.disabled = false;
        submitButton.disabled = false;
    }
}

function disableVotingButtons() {
    const buttons = document.querySelectorAll('.agent-button');
    console.log(buttons);
    buttons.forEach(button => {
        button.disabled = true;
    });
}

function clearPreviousRoundData() {

    const descriptionLog = document.getElementById('description-log');
    if (descriptionLog) {
        descriptionLog.innerHTML = "";
    }

    const descriptionLogContainer = document.getElementById("description-log-container");
    if (descriptionLogContainer) {
        descriptionLogContainer.classList.remove('visible');
    }
}

function grayOutInactiveAgents(activePlayers) {
    const agentButtons = document.querySelectorAll('.agent-button');
    const agentAvatars = document.querySelectorAll('#agent-display img');

    agentAvatars.forEach(avatar => {
        const playerName = avatar.alt;
        if (!activePlayers.includes(playerName)) {
            // If the player is not on the active list, the avatar turns gray
            avatar.style.filter = "grayscale(100%)";
        }
    });
}



