document.addEventListener('DOMContentLoaded', () => {
    const search = document.querySelector('#panelSearch');
    const filterList = document.querySelector('[data-filter-list]');

    if (search && filterList) {
        search.addEventListener('input', () => {
            const query = search.value.trim().toLocaleLowerCase('tr-TR');
            filterList.querySelectorAll('[data-filter-item]').forEach((item) => {
                const text = item.dataset.filterItem.toLocaleLowerCase('tr-TR');
                item.hidden = query && !text.includes(query);
            });
        });
    }

    document.querySelectorAll('form[data-confirm]').forEach((form) => {
        form.addEventListener('submit', (event) => {
            if (!window.confirm(form.dataset.confirm)) {
                event.preventDefault();
            }
        });
    });

    document.querySelectorAll('[data-image-preview]').forEach((preview) => {
        const input = preview.previousElementSibling?.querySelector('input[type="file"]');
        if (!input) {
            return;
        }

        input.addEventListener('change', () => {
            const file = input.files?.[0];
            if (!file) {
                return;
            }

            const imageUrl = URL.createObjectURL(file);
            preview.innerHTML = '';
            const image = document.createElement('img');
            image.src = imageUrl;
            image.alt = 'Seçilen görsel önizlemesi';
            image.onload = () => URL.revokeObjectURL(imageUrl);
            preview.appendChild(image);
        });
    });
});
