// Cart System Logic
document.addEventListener('DOMContentLoaded', () => {
    // State
    let cart = JSON.parse(localStorage.getItem('nodus_cart')) || [];
    
    // DOM Elements
    const cartToggle = document.getElementById('cart-toggle');
    const closeCart = document.getElementById('close-cart');
    const cartDrawer = document.getElementById('cart-drawer');
    const cartOverlay = document.getElementById('cart-overlay');
    const cartBadge = document.getElementById('cart-badge');
    const cartContainer = document.getElementById('cart-items-container');
    const cartTotalPrice = document.getElementById('cart-total-price');
    const checkoutBtn = document.getElementById('checkout-btn');

    // Drawer Logic
    const openDrawer = () => {
        cartDrawer.classList.add('active');
        cartOverlay.classList.add('active');
        document.body.style.overflow = 'hidden';
        renderCart();
    };

    const closeDrawer = () => {
        cartDrawer.classList.remove('active');
        cartOverlay.classList.remove('active');
        document.body.style.overflow = '';
    };

    if (cartToggle) cartToggle.addEventListener('click', openDrawer);
    if (closeCart) closeCart.addEventListener('click', closeDrawer);
    if (cartOverlay) cartOverlay.addEventListener('click', closeDrawer);

    // Cart Logic
    const saveCart = () => {
        localStorage.setItem('nodus_cart', JSON.stringify(cart));
        updateBadge();
    };

    const updateBadge = () => {
        const totalItems = cart.reduce((sum, item) => sum + item.quantity, 0);
        if (cartBadge) {
            cartBadge.textContent = totalItems;
            if (totalItems > 0) {
                cartBadge.classList.add('pop');
                setTimeout(() => cartBadge.classList.remove('pop'), 300);
            }
        }
    };

    window.addToCart = (id, name, price, imagePath) => {
        const existing = cart.find(i => i.id === id);
        if (existing) {
            existing.quantity += 1;
        } else {
            cart.push({ id, name, price: parseFloat(price), imagePath, quantity: 1 });
        }
        saveCart();
        openDrawer();
    };

    const updateQuantity = (id, change) => {
        const item = cart.find(i => i.id === id);
        if (item) {
            item.quantity += change;
            if (item.quantity <= 0) {
                cart = cart.filter(i => i.id !== id);
            }
            saveCart();
            renderCart();
        }
    };

    const renderCart = () => {
        if (!cartContainer) return;
        
        if (cart.length === 0) {
            cartContainer.innerHTML = '<div class="empty-cart-msg">Your cart is empty. Time for coffee!</div>';
            if (checkoutBtn) checkoutBtn.disabled = true;
            if (cartTotalPrice) cartTotalPrice.textContent = '₹0.00';
            return;
        }

        let html = '';
        let total = 0;

        cart.forEach(item => {
            total += item.price * item.quantity;
            html += `
                <div class="cart-item">
                    <img src="${item.imagePath || '/static/images/default_item.png'}" alt="${item.name}" class="cart-item-img">
                    <div class="cart-item-details">
                        <div class="cart-item-title">${item.name}</div>
                        <div class="cart-item-price">₹${item.price}</div>
                        <div class="cart-item-controls">
                            <button class="qty-btn" onclick="updateQuantity(${item.id}, -1)">-</button>
                            <span class="cart-item-qty">${item.quantity}</span>
                            <button class="qty-btn" onclick="updateQuantity(${item.id}, 1)">+</button>
                        </div>
                    </div>
                </div>
            `;
        });

        cartContainer.innerHTML = html;
        if (cartTotalPrice) cartTotalPrice.textContent = `₹${total.toFixed(2)}`;
        if (checkoutBtn) checkoutBtn.disabled = false;
    };

    // Make updateQuantity global so inline handlers can call it
    window.updateQuantity = updateQuantity;

    // Checkout Form
    if (checkoutBtn) {
        checkoutBtn.addEventListener('click', () => {
            renderCheckoutForm();
        });
    }

    const renderCheckoutForm = () => {
        if (!cartContainer) return;
        
        cartContainer.innerHTML = `
            <h3>Guest Checkout</h3>
            <p class="text-muted" style="margin-bottom:1.5rem;font-size:0.9rem;">Please enter your details to place the order.</p>
            <div class="checkout-form">
                <input type="text" id="co-name" placeholder="Full Name" required>
                <input type="text" id="co-phone" placeholder="Phone Number" required>
                <select id="co-type">
                    <option value="dine_in">Dine In</option>
                    <option value="takeaway">Takeaway</option>
                </select>
                <input type="text" id="co-table" placeholder="Table Number (Optional)">
                <button class="btn btn-secondary mt-2" onclick="submitOrder()">Place Order</button>
                <button class="btn" style="background:transparent;border:1px solid rgba(255,255,255,0.2);color:white;" onclick="renderCart()">Back to Cart</button>
            </div>
        `;
        if (checkoutBtn) checkoutBtn.style.display = 'none';
    };

    window.submitOrder = async () => {
        const name = document.getElementById('co-name').value.trim();
        const phone = document.getElementById('co-phone').value.trim();
        const type = document.getElementById('co-type').value;
        const table = document.getElementById('co-table').value.trim();

        if (!name || !phone) {
            alert('Please provide your name and phone number.');
            return;
        }

        const items = cart.map(i => ({ menu_item_id: i.id, quantity: i.quantity, notes: '' }));

        try {
            const response = await fetch('/api/public/orders', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    customer_name: name,
                    table_number: type === 'dine_in' ? table : 'Takeaway',
                    items: items
                })
            });

            if (response.ok) {
                cart = [];
                saveCart();
                cartContainer.innerHTML = `
                    <div style="text-align:center; padding: 2rem 0;">
                        <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="var(--accent-primary)" stroke-width="2" style="margin-bottom:1rem;">
                            <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
                            <polyline points="22 4 12 14.01 9 11.01"></polyline>
                        </svg>
                        <h3>Order Received!</h3>
                        <p class="text-muted">Your order has been sent to our kitchen. We'll have it ready shortly.</p>
                        <button class="btn btn-primary mt-3" onclick="document.getElementById('close-cart').click()">Continue Browsing</button>
                    </div>
                `;
                if (cartTotalPrice) cartTotalPrice.textContent = '₹0.00';
            } else {
                const err = await response.json();
                alert(err.error || 'Failed to place order');
            }
        } catch (e) {
            console.error(e);
            alert('Network error placing order');
        }
    };

    // Initialize Badge on Load
    updateBadge();
});
