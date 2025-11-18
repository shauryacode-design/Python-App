document.addEventListener('DOMContentLoaded', function(){
    const propertyEl = document.getElementById('property-data');
    if (!propertyEl) return;
    const data = propertyEl.dataset;
    const pricePerSqYard = parseFloat(data.price) || 0;
    const length = parseFloat(data.length) || 0;
    const width = parseFloat(data.width) || 0;

    const area = length * width || 0;
    const areaSqYard = area / 9.0;
    function draw(){
        const canvas = document.getElementById('plot');
        if (!canvas) return;
        const ctx = canvas.getContext('2d');
        canvas.width = canvas.offsetWidth;
        canvas.height = 400;

        if (!length || !width || length <= 0 || width <= 0) {
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            ctx.fillStyle = '#ddd';
            ctx.fillRect(0, 0, canvas.width, canvas.height);
            ctx.fillStyle = '#333';
            ctx.font = '18px Arial';
            ctx.textAlign = 'center';
            ctx.fillText('Dimensions not available', canvas.width / 2, canvas.height / 2);
            return;
        }

        const scale = Math.min((canvas.width - 100) / length, (canvas.height - 100) / width) || 1;
        const x = (canvas.width - length * scale) / 2;
        const y = (canvas.height - width * scale) / 2;

        ctx.fillStyle = '#432818';
        ctx.fillRect(x, y, length * scale, width * scale);
        ctx.strokeStyle = '#333';
        ctx.lineWidth = 3;
        ctx.strokeRect(x, y, length * scale, width * scale);

        ctx.fillStyle = '#333';
        ctx.font = '16px Arial';
        ctx.textAlign = 'center';
        ctx.fillText(length + ' ft', x + (length * scale) / 2, y - 10);
    }

    function calcPrice(){
        const areaInput = document.getElementById('customArea');
        const resEl = document.getElementById('result');
        const a = parseFloat(areaInput ? areaInput.value : 0) || 0;
        const total = a * pricePerSqYard;
        if (resEl) resEl.textContent = '₹' + (total / 100000).toFixed(2) + 'L';
    }

    window.calcPrice = calcPrice;
    window.contact = function(){
        const propId = parseInt(propertyEl.dataset.propId) || null;
        const msg = prompt('Enter your message:');
        if (!msg) return;
        fetch('/api/inquiry', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ property_id: propId, message: msg })
        })
        .then(r => r.json())
        .then(d => alert(d.success ? 'Sent!' : (d.error || 'Failed')))
        .catch(e => alert('Error'));
    };

    calcPrice();
    draw();
});