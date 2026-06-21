document.addEventListener('DOMContentLoaded', () => {
    // Utility for fetching data
    async function fetchData(url) {
        try {
            const res = await fetch(url);
            return await res.json();
        } catch (e) {
            console.error('Error fetching data:', e);
            return null;
        }
    }

    // Orders Page Logic
    const ordersList = document.getElementById('ordersList');
    if (ordersList) {
        loadOrders();
        
        document.getElementById('statusFilter').addEventListener('change', loadOrders);
        document.getElementById('dateFilter').addEventListener('change', loadOrders);

        async function loadOrders() {
            const status = document.getElementById('statusFilter').value;
            const date = document.getElementById('dateFilter').value;
            
            let url = '/api/orders?per_page=50';
            if (status) url += `&status=${status}`;
            if (date) url += `&date=${date}`;

            const data = await fetchData(url);
            if (!data || !data.orders) return;

            ordersList.innerHTML = data.orders.map(order => `
                <tr>
                    <td>${order.order_ref}</td>
                    <td>${new Date(order.created_at).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}</td>
                    <td>${order.customer_name}</td>
                    <td>${order.items.length} items</td>
                    <td>₹${order.total_amount}</td>
                    <td>
                        <select onchange="updateOrderStatus(${order.id}, this.value)" class="form-control" style="padding: 0.2rem; width: 120px;">
                            <option value="received" ${order.status === 'received' ? 'selected' : ''}>Received</option>
                            <option value="preparing" ${order.status === 'preparing' ? 'selected' : ''}>Preparing</option>
                            <option value="ready" ${order.status === 'ready' ? 'selected' : ''}>Ready</option>
                            <option value="completed" ${order.status === 'completed' ? 'selected' : ''}>Completed</option>
                            <option value="cancelled" ${order.status === 'cancelled' ? 'selected' : ''}>Cancelled</option>
                        </select>
                    </td>
                    <td>
                        <button class="btn btn-secondary" style="padding: 0.3rem 0.6rem; font-size: 0.8rem;" onclick="deleteOrder(${order.id})">Delete</button>
                    </td>
                </tr>
            `).join('');
            
            if (data.orders.length === 0) {
                ordersList.innerHTML = '<tr><td colspan="7" class="text-center text-muted">No orders found.</td></tr>';
            }
        }
    }

    // Bookings Page Logic
    const bookingsList = document.getElementById('bookingsList');
    if (bookingsList) {
        loadBookings();

        document.getElementById('bookingDateFilter').addEventListener('change', loadBookings);
        document.getElementById('bookingStatusFilter').addEventListener('change', loadBookings);

        async function loadBookings() {
            const date = document.getElementById('bookingDateFilter').value;
            const status = document.getElementById('bookingStatusFilter').value;
            
            let url = '/api/bookings?per_page=50';
            if (date) url += `&date=${date}`;
            if (status) url += `&status=${status}`;

            const data = await fetchData(url);
            if (!data || !data.bookings) return;

            bookingsList.innerHTML = data.bookings.map(b => `
                <tr>
                    <td>${b.booking_ref}</td>
                    <td>${b.time_slot}</td>
                    <td>${b.customer_name}</td>
                    <td>${b.guest_count}</td>
                    <td>
                        <select onchange="updateBookingStatus(${b.id}, this.value)" class="form-control" style="padding: 0.2rem; width: 120px;">
                            <option value="pending" ${b.status === 'pending' ? 'selected' : ''}>Pending</option>
                            <option value="confirmed" ${b.status === 'confirmed' ? 'selected' : ''}>Confirmed</option>
                            <option value="completed" ${b.status === 'completed' ? 'selected' : ''}>Completed</option>
                            <option value="no_show" ${b.status === 'no_show' ? 'selected' : ''}>No Show</option>
                            <option value="cancelled" ${b.status === 'cancelled' ? 'selected' : ''}>Cancelled</option>
                        </select>
                    </td>
                    <td>
                        <button class="btn btn-secondary" style="padding: 0.3rem 0.6rem; font-size: 0.8rem;" onclick="deleteBooking(${b.id})">Cancel</button>
                    </td>
                </tr>
            `).join('');

            if (data.bookings.length === 0) {
                bookingsList.innerHTML = '<tr><td colspan="6" class="text-center text-muted">No bookings found.</td></tr>';
            }
        }
    }

    // ML Predictions Logic
    const activeModelVer = document.getElementById('activeModelVer');
    if (activeModelVer) {
        loadMLData();

        document.getElementById('btnRetrain').addEventListener('click', async () => {
            const log = document.getElementById('mlLog');
            log.innerHTML = 'Training started. This may take a moment...';
            try {
                const res = await fetch('/api/ml/retrain', { method: 'POST' });
                const data = await res.json();
                log.innerHTML = data.success ? `Success: ${data.message}` : `Error: ${data.error}`;
                loadMLData();
            } catch (e) {
                log.innerHTML = 'Network error during retraining.';
            }
        });

        document.getElementById('btnGenerate').addEventListener('click', async () => {
            const log = document.getElementById('mlLog');
            log.innerHTML = 'Generating predictions...';
            try {
                const res = await fetch('/api/ml/generate-predictions', { method: 'POST' });
                const data = await res.json();
                log.innerHTML = data.success ? 'Predictions successfully regenerated for the next 7 days.' : 'Error generating predictions.';
            } catch (e) {
                log.innerHTML = 'Network error.';
            }
        });

        async function loadMLData() {
            const data = await fetchData('/api/ml/models');
            if (!data) return;

            if (data.active_model) {
                activeModelVer.textContent = `v${data.active_model.version_number}`;
                document.getElementById('lastTrained').textContent = new Date(data.active_model.trained_at).toLocaleString();
            } else {
                activeModelVer.textContent = 'None';
                document.getElementById('lastTrained').textContent = 'Never';
            }

            const schedData = await fetchData('/api/ml/scheduler/status');
            if (schedData) {
                document.getElementById('schedulerStatus').textContent = schedData.running ? 'Running' : 'Stopped';
            }

            const modelsList = document.getElementById('modelsList');
            modelsList.innerHTML = data.models.map(m => `
                <tr>
                    <td>v${m.version_number}</td>
                    <td>${new Date(m.trained_at).toLocaleString()}</td>
                    <td>${m.data_points}</td>
                    <td>${m.mae ? m.mae.toFixed(4) : 'N/A'}</td>
                    <td>${m.rmse ? m.rmse.toFixed(4) : 'N/A'}</td>
                    <td><span class="badge ${m.status === 'active' ? 'badge-ready' : 'badge-completed'}">${m.status}</span></td>
                </tr>
            `).join('');
        }
    }

    // Conversations Logic
    const conversationsList = document.getElementById('conversationsList');
    if (conversationsList) {
        loadConversations();
        
        document.getElementById('langFilter').addEventListener('change', loadConversations);
        document.getElementById('searchFilter').addEventListener('input', debounce(loadConversations, 500));

        async function loadConversations() {
            const lang = document.getElementById('langFilter').value;
            const search = document.getElementById('searchFilter').value;
            
            let url = '/api/ai/conversations?per_page=50';
            if (lang) url += `&language=${lang}`;
            if (search) url += `&search=${encodeURIComponent(search)}`;

            const data = await fetchData(url);
            if (!data || !data.conversations) return;

            conversationsList.innerHTML = data.conversations.map(c => `
                <tr>
                    <td><span style="font-family: monospace; font-size:0.8rem;">${c.session_id.substring(0,15)}...</span></td>
                    <td>${c.language.toUpperCase()}</td>
                    <td>${new Date(c.started_at).toLocaleString()}</td>
                    <td>${c.messages ? c.messages.length : 0}</td>
                    <td>
                        <button class="btn btn-secondary" style="padding: 0.3rem 0.6rem; font-size: 0.8rem;" onclick='viewConversation(${JSON.stringify(c).replace(/'/g, "\\'")})'>View</button>
                    </td>
                </tr>
            `).join('');
            
            if (data.conversations.length === 0) {
                conversationsList.innerHTML = '<tr><td colspan="5" class="text-center text-muted">No conversations found.</td></tr>';
            }
        }
    }
});

// Global functions for inline HTML event handlers
window.updateOrderStatus = async function(id, status) {
    try {
        await fetch(`/api/orders/${id}`, {
            method: 'PATCH',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({status})
        });
    } catch (e) {
        console.error('Failed to update status', e);
    }
};

window.deleteOrder = async function(id) {
    if (!confirm('Are you sure you want to delete this order?')) return;
    try {
        await fetch(`/api/orders/${id}`, { method: 'DELETE' });
        location.reload();
    } catch (e) {
        console.error('Failed to delete', e);
    }
};

window.updateBookingStatus = async function(id, status) {
    try {
        await fetch(`/api/bookings/${id}`, {
            method: 'PATCH',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({status})
        });
    } catch (e) {
        console.error('Failed to update status', e);
    }
};

window.deleteBooking = async function(id) {
    if (!confirm('Are you sure you want to cancel this booking?')) return;
    try {
        await fetch(`/api/bookings/${id}`, { method: 'DELETE' });
        location.reload();
    } catch (e) {
        console.error('Failed to cancel', e);
    }
};

window.viewConversation = function(conv) {
    const modal = document.getElementById('convModal');
    const msgContainer = document.getElementById('convMessages');
    
    modal.style.display = 'flex';
    msgContainer.innerHTML = '';
    
    if (!conv.messages || conv.messages.length === 0) {
        msgContainer.innerHTML = '<p class="text-muted">No messages in this conversation.</p>';
        return;
    }
    
    conv.messages.forEach(m => {
        const isUser = m.sender === 'user';
        const wrapper = document.createElement('div');
        wrapper.style.marginBottom = '1rem';
        wrapper.style.textAlign = isUser ? 'right' : 'left';
        
        const bubble = document.createElement('div');
        bubble.style.display = 'inline-block';
        bubble.style.maxWidth = '80%';
        bubble.style.padding = '0.8rem';
        bubble.style.borderRadius = '8px';
        bubble.style.background = isUser ? 'var(--accent-primary)' : 'rgba(255,255,255,0.05)';
        bubble.style.textAlign = 'left';
        
        const textP = document.createElement('p');
        textP.style.margin = '0';
        textP.style.fontSize = '0.9rem';
        textP.textContent = m.message;
        
        const timeSmall = document.createElement('small');
        timeSmall.style.color = 'rgba(255,255,255,0.5)';
        timeSmall.style.fontSize = '0.7rem';
        timeSmall.style.display = 'block';
        timeSmall.style.marginTop = '5px';
        timeSmall.textContent = new Date(m.timestamp).toLocaleTimeString();
        
        bubble.appendChild(textP);
        bubble.appendChild(timeSmall);
        wrapper.appendChild(bubble);
        msgContainer.appendChild(wrapper);
    });
};

window.openNewOrderModal = function() {
    document.getElementById('orderModal').style.display = 'flex';
    // Fetch menu items to populate select
    fetch('/api/menu/items')
        .then(r => r.json())
        .then(data => {
            const select = document.getElementById('orderItems');
            select.innerHTML = data.items.map(item => `<option value="${item.id}">${item.name} - ₹${item.price}</option>`).join('');
        });
};

document.getElementById('newOrderForm')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    const customer = document.getElementById('orderCustomer').value;
    const select = document.getElementById('orderItems');
    const selectedOptions = Array.from(select.selectedOptions);
    
    if (selectedOptions.length === 0) {
        alert('Please select at least one item');
        return;
    }
    
    const items = selectedOptions.map(opt => ({
        menu_item_id: parseInt(opt.value),
        quantity: 1
    }));
    
    try {
        await fetch('/api/orders', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ customer_name: customer, items: items })
        });
        location.reload();
    } catch (err) {
        console.error(err);
        alert('Failed to create order');
    }
});

function debounce(func, wait) {
    let timeout;
    return function(...args) {
        clearTimeout(timeout);
        timeout = setTimeout(() => func.apply(this, args), wait);
    };
}
