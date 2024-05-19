
document.addEventListener('DOMContentLoaded', () => {
    const canvas = document.getElementById('neon-brush-canvas');
    const ctx = canvas.getContext('2d');

    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;

    const colors = ['#ff00ff', '#00ffff', '#ffff00', '#ff00ff', '#00ff00'];
    let mouse = { x: 0, y: 0 };
    let drawing = false;

    // Adjust canvas size on window resize
    window.addEventListener('resize', () => {
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
    });

    // Neon brush function
    function drawNeonLine(x1, y1, x2, y2) {
        ctx.globalCompositeOperation = 'lighter';
        for (let i = 0; i < colors.length; i++) {
            ctx.strokeStyle = colors[i];
            ctx.lineWidth = 5 + i * 2;
            ctx.beginPath();
            ctx.moveTo(x1, y1);
            ctx.lineTo(x2, y2);
            ctx.stroke();
        }
        ctx.globalCompositeOperation = 'source-over';
    }

    // Event listeners for mouse movements
    canvas.addEventListener('mousedown', (e) => {
        mouse.x = e.clientX;
        mouse.y = e.clientY;
        drawing = true;
    });

    canvas.addEventListener('mousemove', (e) => {
        if (!drawing) return;
        const x = e.clientX;
        const y = e.clientY;
        drawNeonLine(mouse.x, mouse.y, x, y);
        mouse.x = x;
        mouse.y = y;
    });

    canvas.addEventListener('mouseup', () => {
        drawing = false;
    });

    canvas.addEventListener('mouseout', () => {
        drawing = false;
    });

});