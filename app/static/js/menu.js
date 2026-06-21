document.addEventListener('DOMContentLoaded', () => {
    const searchInput = document.getElementById('menuSearch');
    const filterBtns = document.querySelectorAll('.cat-pill');
    const menuItems = document.querySelectorAll('.menu-item-card');
    const noResults = document.getElementById('noResults');

    let currentCategory = 'all';
    let searchQuery = '';

    // Search input event
    if (searchInput) {
        searchInput.addEventListener('input', (e) => {
            searchQuery = e.target.value.toLowerCase();
            filterMenu();
        });
    }

    // Filter button click events
    filterBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            // Update active state
            filterBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            
            currentCategory = btn.getAttribute('data-filter');
            filterMenu();
        });
    });

    function filterMenu() {
        let visibleCount = 0;

        menuItems.forEach(item => {
            const itemCat = item.getAttribute('data-category');
            const itemName = item.querySelector('.item-name').textContent.toLowerCase();
            const itemDesc = item.querySelector('.item-desc').textContent.toLowerCase();
            
            const matchesCat = currentCategory === 'all' || itemCat === currentCategory;
            const matchesSearch = itemName.includes(searchQuery) || itemDesc.includes(searchQuery);

            if (matchesCat && matchesSearch) {
                item.classList.remove('hidden');
                visibleCount++;
            } else {
                item.classList.add('hidden');
            }
        });

        if (visibleCount === 0) {
            noResults.classList.remove('hidden');
        } else {
            noResults.classList.add('hidden');
        }
    }
});
