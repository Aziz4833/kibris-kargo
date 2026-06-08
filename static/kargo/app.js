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

    document.querySelectorAll('[data-dynamic-fields]').forEach((container) => {
        const hiddenInput = container.querySelector('input[type="hidden"]');
        const list = container.querySelector('[data-dynamic-field-list]');
        const addButton = container.querySelector('[data-add-dynamic-field]');
        const categoryInput = document.querySelector('#id_kategori');
        const templates = {
            giyim: {
                label: 'Kıyafet',
                fields: ['Beden', 'Renk', 'Kumaş', 'Kalıp', 'Cinsiyet'],
            },
            ayakkabi: {
                label: 'Ayakkabı',
                fields: ['Numara', 'Renk', 'Materyal', 'Taban', 'Cinsiyet'],
            },
            teknoloji: {
                label: 'Teknoloji',
                fields: ['Marka', 'Model', 'Garanti', 'Durum', 'Teknik özellik'],
            },
            ev: {
                label: 'Ev ve yaşam',
                fields: ['Ölçü', 'Malzeme', 'Kullanım alanı', 'Renk'],
            },
            ozel: {
                label: '',
                fields: [],
            },
        };

        const readInitialFields = () => {
            if (!hiddenInput?.value) {
                return {};
            }

            try {
                const parsed = JSON.parse(hiddenInput.value);
                return parsed && typeof parsed === 'object' && !Array.isArray(parsed) ? parsed : {};
            } catch {
                return {};
            }
        };

        const syncHiddenInput = () => {
            const data = {};
            list.querySelectorAll('[data-dynamic-field-row]').forEach((row) => {
                const key = row.querySelector('[data-dynamic-key]')?.value.trim();
                const value = row.querySelector('[data-dynamic-value]')?.value.trim();
                if (key && value) {
                    data[key] = value;
                }
            });
            hiddenInput.value = JSON.stringify(data);
        };

        const addRow = (key = '', value = '') => {
            const row = document.createElement('div');
            row.className = 'dynamic-field-row';
            row.dataset.dynamicFieldRow = 'true';
            row.innerHTML = `
                <input data-dynamic-key type="text" placeholder="Alan adı" value="${escapeAttribute(key)}">
                <input data-dynamic-value type="text" placeholder="Değer" value="${escapeAttribute(value)}">
                <button class="button danger" type="button" data-remove-dynamic-field>Sil</button>
            `;
            row.querySelectorAll('input').forEach((input) => input.addEventListener('input', syncHiddenInput));
            row.querySelector('[data-remove-dynamic-field]').addEventListener('click', () => {
                row.remove();
                syncHiddenInput();
            });
            list.appendChild(row);
            syncHiddenInput();
        };

        const hasField = (key) => {
            const normalizedKey = key.toLocaleLowerCase('tr-TR');
            return Array.from(list.querySelectorAll('[data-dynamic-key]')).some((input) => (
                input.value.trim().toLocaleLowerCase('tr-TR') === normalizedKey
            ));
        };

        const applyTemplate = (templateKey) => {
            const template = templates[templateKey];
            if (!template) {
                return;
            }

            if (categoryInput && template.label) {
                categoryInput.value = template.label;
            }

            if (templateKey === 'ozel') {
                if (!list.querySelector('[data-dynamic-field-row]')) {
                    addRow();
                }
                return;
            }

            template.fields.forEach((field) => {
                if (!hasField(field)) {
                    addRow(field, '');
                }
            });
        };

        const currentFields = readInitialFields();
        Object.entries(currentFields).forEach(([key, value]) => addRow(key, value));

        if (!Object.keys(currentFields).length) {
            addRow();
        }

        addButton?.addEventListener('click', () => addRow());

        document.querySelectorAll('[data-product-template]').forEach((button) => {
            button.addEventListener('click', () => applyTemplate(button.dataset.productTemplate));
        });

        const urlTemplate = new URLSearchParams(window.location.search).get('sablon');
        if (urlTemplate) {
            applyTemplate(urlTemplate);
        }

        container.querySelectorAll('[data-suggestion-group]').forEach((button) => {
            button.addEventListener('click', () => {
                applyTemplate(button.dataset.suggestionGroup);
            });
        });
    });

    document.querySelectorAll('[data-tax-panel]').forEach((panel) => {
        const priceInput = document.querySelector('#id_fiyat');
        const taxInput = panel.querySelector('#id_vergi_orani');
        const totalOutput = panel.querySelector('[data-tax-total]');
        const applyButton = panel.querySelector('[data-apply-tax-price]');

        if (!priceInput || !taxInput || !totalOutput) {
            return;
        }

        const parseDecimal = (value) => {
            const parsed = Number.parseFloat(String(value || '').replace(',', '.'));
            return Number.isFinite(parsed) ? parsed : 0;
        };

        const calculateTotal = () => {
            const price = parseDecimal(priceInput.value);
            const taxRate = parseDecimal(taxInput.value);
            const total = price + (price * taxRate / 100);
            totalOutput.textContent = `${total.toFixed(2)} TL`;
            return total;
        };

        priceInput.addEventListener('input', calculateTotal);
        taxInput.addEventListener('input', calculateTotal);
        applyButton?.addEventListener('click', () => {
            priceInput.value = calculateTotal().toFixed(2);
        });
        calculateTotal();
    });
});

function escapeAttribute(value) {
    return String(value)
        .replaceAll('&', '&amp;')
        .replaceAll('"', '&quot;')
        .replaceAll('<', '&lt;')
        .replaceAll('>', '&gt;');
}
