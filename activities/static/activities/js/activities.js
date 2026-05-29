(function () {
    const companySelect = document.getElementById('id_company');
    const projectSelect = document.getElementById('id_project');
    if (!companySelect || !projectSelect) return;

    // Snapshot all options once at load time (includes data-company-id attributes)
    const snapshot = Array.from(projectSelect.options).map(function (o) {
        return {
            value: o.value,
            text: o.text,
            companyId: o.getAttribute('data-company-id') || '',
        };
    });

    function filterProjects() {
        const companyId = companySelect.value;
        const current = projectSelect.value;

        projectSelect.innerHTML = '';
        snapshot.forEach(function (item) {
            if (!item.value || !companyId || item.companyId === companyId) {
                const opt = document.createElement('option');
                opt.value = item.value;
                opt.textContent = item.text;
                if (item.companyId) opt.setAttribute('data-company-id', item.companyId);
                projectSelect.appendChild(opt);
            }
        });

        // Restore previous selection if it still belongs to the current company
        projectSelect.value = current;
    }

    companySelect.addEventListener('change', filterProjects);
    filterProjects(); // run on page load so the list is already filtered
})();
