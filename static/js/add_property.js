function calc(){
    const length = parseFloat(document.getElementById('length').value) || 0;
    const width = parseFloat(document.getElementById('width').value) || 0;
    const price = parseFloat(document.getElementById('price').value) || 0;
    const sqft = length * width;
    const area_sq_yards = sqft / 9.0;
    const total = area_sq_yards * price;
    const areaEl = document.getElementById('area');
    const totalEl = document.getElementById('total');
    if(areaEl) areaEl.innerHTML = `Area: <strong>${sqft.toFixed(2)} sq ft | ${area_sq_yards.toFixed(2)} sq yd</strong>`;
    if(totalEl) totalEl.innerHTML = `Total: <strong>₹${total.toLocaleString('en-IN')}</strong> (₹${(total/100000).toFixed(2)} L)`;
}