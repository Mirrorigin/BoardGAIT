let playerName;

// Initialize fullPage.js
new fullpage('#fullpage', {
    licenseKey: '',
    autoScrolling: true,
    navigation: true,
    onLeave: (origin, destination, direction) => {
        // Prevents access to the second screen if the player name is not entered
        if (destination.index === 1 && !playerName) {
            showFlashMessage('Please enter your name before proceeding.');
            return false;
        }
    }
});

function showFlashMessage(message) {
    const flash = document.getElementById('flash-message');
    flash.textContent = message;
    flash.classList.add('show');

    setTimeout(() => {
        flash.classList.remove('show');
    }, 3000);
}

// Player joins the game
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

    // Send a request to join the game and initialize the game
    try {
        const response = await fetch('/join_game', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ player: playerName })
        });

        const data = await response.json();

        // Wait for the server to respond...
        if (response.ok) {
            console.log("Game initialized successfully!");

            updatePlayerList(data.players); // Update the player list

            document.getElementById('start-game-button').disabled = false;  // Enable the Start_Game button
        } else {
            errorMessage.textContent = data.error;
            fullpage_api.moveSectionUp();
        }
    } catch (error) {
        console.error("Error during join game:", error);
        errorMessage.textContent = "An error occurred. Please try again.";
        fullpage_api.moveSectionUp();
    }
}

async function startGame() {
    window.location.href = '/game';
}

function moveToNextStep() {
    fullpage_api.moveSectionDown();
}

function updatePlayerList(players) {
    const playerList = document.getElementById('player-list');
    playerList.innerHTML = '';

    players.forEach(player => {
        const listItem = document.createElement('li');
        listItem.textContent = player;
        playerList.appendChild(listItem);
     });
}

// 模拟 Agent 数据
const agents = [
    { name: "Agent Alpha", avatar: "https://via.placeholder.com/150" },
    { name: "Agent Bravo", avatar: "https://via.placeholder.com/150" },
    { name: "Agent Charlie", avatar: "https://via.placeholder.com/150" },
    { name: "Agent Delta", avatar: "https://via.placeholder.com/150" }
];

// 动态显示 Agents
function displayAgents(agents) {
    const container = document.getElementById('agent-display');
    container.innerHTML = ""; // 确保容器是空的

    let index = 0;

    function showNextAgent() {
        if (index >= agents.length) return; // 所有 Agent 显示完成

        const agent = agents[index];

        // 创建 Agent 头像和名字元素
        const agentElement = document.createElement('div');
        agentElement.style.textAlign = "center";

        const avatar = document.createElement('img');
        avatar.src = agent.avatar;
        avatar.alt = agent.name;
        avatar.style.width = "100px";
        avatar.style.height = "100px";
        avatar.style.borderRadius = "50%"; // 圆形头像

        const name = document.createElement('p');
        name.textContent = agent.name;
        name.style.marginTop = "10px";

        // 将头像和名字添加到 Agent 元素
        agentElement.appendChild(avatar);
        agentElement.appendChild(name);

        // 将 Agent 元素添加到容器中
        container.appendChild(agentElement);

        index++; // 显示下一个 Agent
        setTimeout(showNextAgent, 1000); // 间隔 1 秒显示下一个
    }

    showNextAgent(); // 开始显示第一个 Agent
}

// 调用函数显示 Agents
displayAgents(agents);