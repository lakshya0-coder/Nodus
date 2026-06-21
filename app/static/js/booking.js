document.addEventListener('DOMContentLoaded', () => {
    const dateInput = document.getElementById('bookingDate');
    const timeSlotsGrid = document.getElementById('timeSlotsGrid');
    const selectedSlotInput = document.getElementById('selectedSlot');
    const bookingForm = document.getElementById('bookingForm');
    
    // Auto-load today's slots
    if (dateInput.value) {
        fetchSlots(dateInput.value);
    } else {
        const today = new Date().toISOString().split('T')[0];
        dateInput.value = today;
        fetchSlots(today);
    }

    dateInput.addEventListener('change', (e) => {
        fetchSlots(e.target.value);
    });

    async function fetchSlots(dateStr) {
        timeSlotsGrid.innerHTML = '<p class="text-muted" style="grid-column: 1/-1;">Loading slots...</p>';
        selectedSlotInput.value = '';
        
        try {
            const res = await fetch(`/api/bookings/availability?date=${dateStr}`);
            const data = await res.json();
            
            if (data.error) {
                timeSlotsGrid.innerHTML = `<p class="text-error" style="grid-column: 1/-1;">${data.error}</p>`;
                return;
            }
            
            renderSlots(data.slots);
        } catch (err) {
            timeSlotsGrid.innerHTML = '<p class="text-error" style="grid-column: 1/-1;">Failed to load availability.</p>';
        }
    }

    function renderSlots(slots) {
        if (!slots || slots.length === 0) {
            timeSlotsGrid.innerHTML = '<p class="text-muted" style="grid-column: 1/-1;">No slots available for this date.</p>';
            return;
        }

        timeSlotsGrid.innerHTML = '';
        
        slots.forEach(slot => {
            const btn = document.createElement('button');
            btn.type = 'button';
            btn.className = 'slot-btn';
            
            // Format time for display (e.g. "08:00")
            const displayTime = slot.label.split(' - ')[0];
            
            let label = slot.predicted_label || 'moderate';
            if (slot.is_full) {
                btn.disabled = true;
                label = 'full';
            }
            
            btn.innerHTML = `
                ${displayTime}
                <span class="slot-indicator ${label}"></span>
            `;
            
            btn.addEventListener('click', () => {
                // Remove selected from all
                document.querySelectorAll('.slot-btn').forEach(b => b.classList.remove('selected'));
                btn.classList.add('selected');
                selectedSlotInput.value = slot.time_slot;
            });
            
            timeSlotsGrid.appendChild(btn);
        });
    }

    // Form Submission
    bookingForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        if (!selectedSlotInput.value) {
            showToast('Please select a time slot', 'error');
            return;
        }

        const submitBtn = document.getElementById('submitBtn');
        submitBtn.disabled = true;
        submitBtn.textContent = 'Booking...';

        const payload = {
            date: dateInput.value,
            time_slot: selectedSlotInput.value,
            guest_count: parseInt(document.getElementById('guestCount').value),
            customer_name: document.getElementById('customerName').value,
            customer_phone: document.getElementById('customerPhone').value,
            seating_preference: document.querySelector('input[name="seating"]:checked').value
        };

        try {
            const res = await fetch('/api/bookings', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            
            const data = await res.json();
            
            if (res.ok) {
                // Success
                bookingForm.classList.add('hidden');
                const successDiv = document.getElementById('bookingSuccess');
                document.getElementById('successRef').textContent = data.booking.booking_ref;
                successDiv.classList.remove('hidden');
            } else {
                showToast(data.error || 'Failed to book slot', 'error');
                submitBtn.disabled = false;
                submitBtn.textContent = 'Confirm Booking';
            }
        } catch (err) {
            showToast('Network error occurred', 'error');
            submitBtn.disabled = false;
            submitBtn.textContent = 'Confirm Booking';
        }
    });
});
