<!DOCTYPE html>
<html lang="de">
<head>
  <meta charset="UTF-8">
  <title>Advanced Snake Game – Segment-Wachstum</title>
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <style>
    body { 
      margin: 0; 
      background: #111; 
      display: flex; 
      justify-content: center; 
      align-items: center; 
      height: 100vh; 
      user-select: none; 
      overflow: hidden; 
    }
    canvas { 
      background: #222; 
      border: 2px solid #555; 
      touch-action: none; 
    }
  </style>
</head>
<body>
  <canvas id="gameCanvas" width="1200" height="800"></canvas>
  <script>
    // GRID- UND SPIELKONFIGURATION
    const canvas = document.getElementById("gameCanvas");
    const ctx = canvas.getContext("2d");
    const cellSize = 20;
    const gridWidth = canvas.width / cellSize;   // z.B. 60 Zellen horizontal
    const gridHeight = canvas.height / cellSize;  // z.B. 40 Zellen vertikal
    const TICK_INTERVAL = 150;       // Zeit in ms pro Zug
    const TARGET_APPLE_COUNT = 50;   // Es sollen immer ca. 50 Äpfel vorhanden sein
    const MAX_BOTS = 10;             // Max. Anzahl der Bots
    const BOT_SPAWN_INTERVAL = 15000; // Neuer Bot alle 15 Sek.

    let apples = [];
    let bots = [];
    let gameOver = false;
    let lastBotSpawnTime = Date.now();

    // Spieler-Snake (als Array von Segmenten – jedes Segment hat x,y)
    let player = {
      snake: [
        { x: Math.floor(gridWidth/2), y: Math.floor(gridHeight/2) },
        { x: Math.floor(gridWidth/2)-1, y: Math.floor(gridHeight/2) },
        { x: Math.floor(gridWidth/2)-2, y: Math.floor(gridHeight/2) }
      ],
      direction: { dx: 1, dy: 0 }  // Startbewegung nach rechts
    };

    // Bot-Snake: Jeder Bot ist ein Objekt mit eigener Snake und Richtung
    function createBot() {
      let startX = Math.floor(Math.random() * gridWidth);
      let startY = Math.floor(Math.random() * gridHeight);
      return {
        snake: [
          { x: startX, y: startY },
          { x: startX - 1, y: startY }
        ],
        direction: { dx: 1, dy: 0 }
      };
    }

    // Apfel spawnen: zufällige Zelle
    function spawnApple() {
      let apple = {
        x: Math.floor(Math.random() * gridWidth),
        y: Math.floor(Math.random() * gridHeight)
      };
      apples.push(apple);
    }
    // Sicherstellen, dass immer genügend Äpfel vorhanden sind
    function ensureApples() {
      while(apples.length < TARGET_APPLE_COUNT) {
        spawnApple();
      }
    }

    // Initialisierung: Äpfel und einige Bots erzeugen
    function initGame() {
      apples = [];
      bots = [];
      ensureApples();
      for(let i = 0; i < 3; i++){
        bots.push(createBot());
      }
    }

    // Steuerung: Pfeiltasten und Touch-Swipe für den Spieler
    document.addEventListener("keydown", e => {
      switch(e.key) {
        case "ArrowUp":
          if(player.direction.dy !== 1) player.direction = { dx: 0, dy: -1 };
          break;
        case "ArrowDown":
          if(player.direction.dy !== -1) player.direction = { dx: 0, dy: 1 };
          break;
        case "ArrowLeft":
          if(player.direction.dx !== 1) player.direction = { dx: -1, dy: 0 };
          break;
        case "ArrowRight":
          if(player.direction.dx !== -1) player.direction = { dx: 1, dy: 0 };
          break;
      }
    });
    let touchStartX = 0, touchStartY = 0;
    canvas.addEventListener("touchstart", e => {
      let touch = e.touches[0];
      touchStartX = touch.clientX;
      touchStartY = touch.clientY;
    });
    canvas.addEventListener("touchend", e => {
      let touch = e.changedTouches[0];
      let dx = touch.clientX - touchStartX;
      let dy = touch.clientY - touchStartY;
      if(Math.abs(dx) > Math.abs(dy)){
        if(dx > 0 && player.direction.dx !== -1) player.direction = { dx: 1, dy: 0 };
        else if(dx < 0 && player.direction.dx !== 1) player.direction = { dx: -1, dy: 0 };
      } else {
        if(dy > 0 && player.direction.dy !== -1) player.direction = { dx: 0, dy: 1 };
        else if(dy < 0 && player.direction.dy !== 1) player.direction = { dx: 0, dy: -1 };
      }
    });

    // Hilfsfunktion: Wrap-Around (am Rand erscheint man am gegenüberliegenden Ende)
    function wrapPosition(pos) {
      if(pos.x < 0) pos.x = gridWidth - 1;
      if(pos.x >= gridWidth) pos.x = 0;
      if(pos.y < 0) pos.y = gridHeight - 1;
      if(pos.y >= gridHeight) pos.y = 0;
    }

    // Verschiebe eine Snake: Neuer Kopf wird hinzugefügt; wenn grow nicht true, wird das letzte Segment entfernt
    function moveSnake(snake, direction, grow) {
      let head = snake[0];
      let newHead = { x: head.x + direction.dx, y: head.y + direction.dy };
      wrapPosition(newHead);
      snake.unshift(newHead);
      if(!grow) snake.pop();
    }

    // Spieler aktualisieren
    function updatePlayer() {
      let head = player.snake[0];
      let newHead = { x: head.x + player.direction.dx, y: head.y + player.direction.dy };
      wrapPosition(newHead);
      // Prüfe, ob ein Apfel an der neuen Position liegt
      let ateApple = false;
      for(let i = 0; i < apples.length; i++){
        if(apples[i].x === newHead.x && apples[i].y === newHead.y){
          ateApple = true;
          apples.splice(i, 1);
          break;
        }
      }
      moveSnake(player.snake, player.direction, ateApple);
    }

    // Bots aktualisieren: Jeder Bot sucht sich das nächstgelegene Apfelziel (Manhattan-Distanz)
    function updateBots() {
      bots.forEach(bot => {
        let head = bot.snake[0];
        let target = null, minDist = Infinity;
        apples.forEach(apple => {
          let d = Math.abs(apple.x - head.x) + Math.abs(apple.y - head.y);
          if(d < minDist){
            minDist = d;
            target = apple;
          }
        });
        if(target) {
          let dx = target.x - head.x;
          let dy = target.y - head.y;
          if(Math.abs(dx) > Math.abs(dy))
            bot.direction = { dx: dx > 0 ? 1 : -1, dy: 0 };
          else
            bot.direction = { dx: 0, dy: dy > 0 ? 1 : -1 };
        }
        let nextHead = { x: head.x + bot.direction.dx, y: head.y + bot.direction.dy };
        wrapPosition(nextHead);
        let ateApple = false;
        for(let i = 0; i < apples.length; i++){
          if(apples[i].x === nextHead.x && apples[i].y === nextHead.y){
            ateApple = true;
            apples.splice(i, 1);
            break;
          }
        }
        moveSnake(bot.snake, bot.direction, ateApple);
      });
    }

    // Kollision: Vergleiche die Köpfe – wenn Spieler und Bot auf derselben Zelle landen,
    // frisst der größere (längere Snake) den kleineren; im Falle, dass der Spieler kleiner ist, endet das Spiel.
    function checkCollisions() {
      let pHead = player.snake[0];
      bots.forEach((bot, index) => {
        let bHead = bot.snake[0];
        if(pHead.x === bHead.x && pHead.y === bHead.y){
          if(player.snake.length > bot.snake.length){
            // Spieler frisst den Bot: Füge so viele Segmente hinzu, wie der Bot lang ist
            for(let i = 0; i < bot.snake.length; i++){
              player.snake.push({ ...player.snake[player.snake.length - 1] });
            }
            bots.splice(index, 1);
          } else if(player.snake.length < bot.snake.length){
            gameOver = true;
          }
        }
      });
      // Bots untereinander: Kopf-zu-Kopf Kollisionen
      for(let i = 0; i < bots.length; i++){
        for(let j = i + 1; j < bots.length; j++){
          let headA = bots[i].snake[0];
          let headB = bots[j].snake[0];
          if(headA.x === headB.x && headA.y === headB.y){
            if(bots[i].snake.length > bots[j].snake.length){
              for(let k = 0; k < bots[j].snake.length; k++){
                bots[i].snake.push({ ...bots[i].snake[bots[i].snake.length - 1] });
              }
              bots.splice(j, 1);
              j--;
            } else if(bots[i].snake.length < bots[j].snake.length){
              for(let k = 0; k < bots[i].snake.length; k++){
                bots[j].snake.push({ ...bots[j].snake[bots[j].snake.length - 1] });
              }
              bots.splice(i, 1);
              i--;
              break;
            }
          }
        }
      }
    }

    // Zeichnet eine Zelle als Kreis
    function drawCell(x, y, color) {
      ctx.fillStyle = color;
      ctx.beginPath();
      let cx = x * cellSize + cellSize/2;
      let cy = y * cellSize + cellSize/2;
      let radius = cellSize/2 - 2;
      ctx.arc(cx, cy, radius, 0, 2 * Math.PI);
      ctx.fill();
    }

    function draw() {
      ctx.fillStyle = "#222";
      ctx.fillRect(0, 0, canvas.width, canvas.height);
      // Äpfel zeichnen
      apples.forEach(apple => {
        drawCell(apple.x, apple.y, "green");
      });
      // Spieler-Snake zeichnen (blau)
      player.snake.forEach(seg => {
        drawCell(seg.x, seg.y, "blue");
      });
      // Bot-Snakes zeichnen (rot) und ihren Score (Länge) anzeigen
      bots.forEach(bot => {
        bot.snake.forEach(seg => {
          drawCell(seg.x, seg.y, "red");
        });
        ctx.fillStyle = "white";
        ctx.font = "12px Arial";
        ctx.fillText(bot.snake.length, bot.snake[0].x * cellSize, bot.snake[0].y * cellSize);
      });
      // Spieler-Score
      ctx.fillStyle = "white";
      ctx.font = "20px Arial";
      ctx.fillText("Score: " + player.snake.length, 10, 30);
    }

    function gameTick() {
      if(gameOver) return;
      updatePlayer();
      updateBots();
      checkCollisions();
      ensureApples();
      // Neuer Bot spawnt in regelmäßigen Abständen (falls unter Max)
      if(Date.now() - lastBotSpawnTime > BOT_SPAWN_INTERVAL && bots.length < MAX_BOTS){
        bots.push(createBot());
        lastBotSpawnTime = Date.now();
      }
      draw();
    }

    initGame();
    setInterval(gameTick, TICK_INTERVAL);
  </script>
</body>
</html>
