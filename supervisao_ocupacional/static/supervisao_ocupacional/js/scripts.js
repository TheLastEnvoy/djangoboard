/**
 * Dashboard SO - Scripts Principais
 * Versão: 2.0
 * Data: 27/02/2025
 */

document.addEventListener('DOMContentLoaded', function() {
    console.log('Dashboard carregado com sucesso!');

    // ======== NAVEGAÇÃO E UI ========

    // Destacar o item de menu ativo com efeito visual melhorado
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('.nav-link');

    navLinks.forEach(link => {
        const href = link.getAttribute('href');
        if ((currentPath.includes(href) && href !== '/') || 
            (currentPath === '/' && href === '/')) {
            link.classList.add('active');
            link.classList.add('fw-bold');

            // Adicionar ícone de indicação (opcional)
            const icon = link.querySelector('i');
            if (icon) {
                icon.classList.add('text-primary');
            }

            // Encontrar o item pai para destacar a seção inteira
            const parentItem = link.closest('.nav-item');
            if (parentItem) {
                parentItem.classList.add('menu-active');
            }
        }
    });

    // Toggle para o menu lateral em dispositivos móveis
    const sidebarToggle = document.getElementById('sidebarToggle');
    if (sidebarToggle) {
        sidebarToggle.addEventListener('click', function() {
            document.body.classList.toggle('sidebar-toggled');
            const sidebar = document.querySelector('.sidebar');
            if (sidebar) {
                sidebar.classList.toggle('toggled');
            }
        });
    }

    // Colapsar menu lateral automaticamente em telas pequenas
    function checkScreenSize() {
        if (window.innerWidth < 768) {
            const sidebar = document.querySelector('.sidebar');
            if (sidebar && !sidebar.classList.contains('toggled')) {
                document.body.classList.add('sidebar-toggled');
                sidebar.classList.add('toggled');
            }
        }
    }

    // Verificar tamanho da tela ao carregar e ao redimensionar
    checkScreenSize();
    window.addEventListener('resize', checkScreenSize);

    // ======== COMPONENTES BOOTSTRAP ========

    // Inicializar tooltips do Bootstrap
    if (typeof bootstrap !== 'undefined') {
        // Tooltips
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl, {
                boundary: document.body
            });
        });

        // Popovers
        const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
        popoverTriggerList.map(function (popoverTriggerEl) {
            return new bootstrap.Popover(popoverTriggerEl, {
                html: true,
                sanitize: false
            });
        });

        // Toasts para notificações
        const toastElList = [].slice.call(document.querySelectorAll('.toast'));
        toastElList.map(function (toastEl) {
            return new bootstrap.Toast(toastEl, {
                autohide: true,
                delay: 5000
            }).show();
        });
    }

    // ======== MELHORIAS PARA TABELAS ========

    // Inicializar DataTables com configurações avançadas
    if (typeof $.fn.DataTable !== 'undefined') {
        $('.dataTable').each(function() {
            const tableId = $(this).attr('id');
            const hasExistingDataTable = $.fn.DataTable.isDataTable('#' + tableId);

            if (!hasExistingDataTable) {
                $(this).DataTable({
                    language: {
                        url: "//cdn.datatables.net/plug-ins/1.10.24/i18n/Portuguese-Brasil.json"
                    },
                    responsive: true,
                    pageLength: 10,
                    lengthMenu: [[10, 25, 50, 100, -1], [10, 25, 50, 100, "Todos"]],
                    dom: '<"d-flex justify-content-between align-items-center mb-3"<"d-flex align-items-center"l><"d-flex"f>>t<"d-flex justify-content-between align-items-center mt-3"<"d-flex align-items-center"i><"d-flex"p>>',
                    buttons: [
                        {
                            extend: 'copy',
                            text: 'Copiar',
                            className: 'btn btn-sm btn-outline-secondary'
                        },
                        {
                            extend: 'csv',
                            text: 'CSV',
                            className: 'btn btn-sm btn-outline-secondary'
                        },
                        {
                            extend: 'excel',
                            text: 'Excel',
                            className: 'btn btn-sm btn-outline-secondary'
                        },
                        {
                            extend: 'pdf',
                            text: 'PDF',
                            className: 'btn btn-sm btn-outline-secondary'
                        },
                        {
                            extend: 'print',
                            text: 'Imprimir',
                            className: 'btn btn-sm btn-outline-secondary'
                        }
                    ]
                });

                // Adicionar botões de exportação após a inicialização
                if (typeof $.fn.DataTable.Buttons !== 'undefined') {
                    new $.fn.DataTable.Buttons($(this).DataTable(), {
                        buttons: [
                            'copy', 'csv', 'excel', 'pdf', 'print'
                        ]
                    });

                    $(this).DataTable().buttons().container()
                        .appendTo('#' + tableId + '_wrapper .dt-buttons');
                }
            }
        });
    }

    // ======== MELHORIAS PARA GRÁFICOS ========

    // Função para ajustar gráficos Plotly ao tema
    function applyPlotlyTheme() {
        const isDarkMode = document.body.classList.contains('dark-mode');
        const textColor = isDarkMode ? '#e0e0e0' : '#333333';
        const gridColor = isDarkMode ? '#444444' : '#e0e0e0';
        const paperBgColor = isDarkMode ? '#2a2a2a' : '#ffffff';
        const plotBgColor = isDarkMode ? '#2a2a2a' : '#ffffff';

        // Aplicar tema a todos os gráficos Plotly
        const plotlyCharts = document.querySelectorAll('[id$="-chart"]');
        plotlyCharts.forEach(chart => {
            if (chart && chart.id) {
                Plotly.relayout(chart.id, {
                    'paper_bgcolor': paperBgColor,
                    'plot_bgcolor': plotBgColor,
                    'font.color': textColor,
                    'xaxis.gridcolor': gridColor,
                    'yaxis.gridcolor': gridColor,
                    'xaxis.color': textColor,
                    'yaxis.color': textColor
                });
            }
        });
    }

    // Aplicar tema aos gráficos se o Plotly estiver disponível
    if (typeof Plotly !== 'undefined') {
        // Configurar responsividade para todos os gráficos
        window.addEventListener('resize', function() {
            const charts = document.querySelectorAll('[id$="-chart"]');
            charts.forEach(function(chart) {
                if (chart && chart.id) {
                    Plotly.relayout(chart.id, {
                        'width': chart.offsetWidth,
                        'height': chart.offsetHeight
                    });
                }
            });
        });

        // Aplicar tema inicial
        applyPlotlyTheme();

        // Adicionar botões de download para gráficos
        const charts = document.querySelectorAll('[id$="-chart"]');
        charts.forEach(function(chart) {
            if (chart && chart.id) {
                const chartContainer = chart.closest('.card-body');
                if (chartContainer) {
                    const downloadBtn = document.createElement('button');
                    downloadBtn.className = 'btn btn-sm btn-outline-secondary chart-download-btn';
                    downloadBtn.innerHTML = '<i class="fas fa-download"></i> Baixar';
                    downloadBtn.style.position = 'absolute';
                    downloadBtn.style.top = '10px';
                    downloadBtn.style.right = '10px';
                    downloadBtn.style.zIndex = '100';
                    downloadBtn.style.opacity = '0.7';
                    downloadBtn.addEventListener('mouseenter', function() {
                        this.style.opacity = '1';
                    });
                    downloadBtn.addEventListener('mouseleave', function() {
                        this.style.opacity = '0.7';
                    });
                    downloadBtn.addEventListener('click', function() {
                        Plotly.downloadImage(chart.id, {
                            format: 'png',
                            filename: chart.id,
                            width: chart.offsetWidth * 2,
                            height: chart.offsetHeight * 2,
                            scale: 2
                        });
                    });

                    chartContainer.style.position = 'relative';
                    chartContainer.appendChild(downloadBtn);
                }
            }
        });
    }

    // ======== FILTROS AVANÇADOS ========

    // Melhorar os selects com Select2 se disponível
    if (typeof $.fn.select2 !== 'undefined') {
        $('.form-control:not(.dataTables_length select)').select2({
            theme: 'bootstrap-5',
            width: '100%',
            placeholder: 'Selecione uma opção',
            allowClear: true
        });
    }

    // Adicionar datepickers para campos de data
    if (typeof $.fn.datepicker !== 'undefined') {
        $('.date-picker').datepicker({
            format: 'dd/mm/yyyy',
            language: 'pt-BR',
            autoclose: true,
            todayHighlight: true
        });
    }

    // Adicionar funcionalidade de filtro rápido
    const quickFilterInput = document.getElementById('quickFilter');
    if (quickFilterInput) {
        quickFilterInput.addEventListener('keyup', function() {
            const filterValue = this.value.toLowerCase();
            const tableRows = document.querySelectorAll('.table tbody tr');

            tableRows.forEach(row => {
                const text = row.textContent.toLowerCase();
                row.style.display = text.includes(filterValue) ? '' : 'none';
            });
        });
    }

    // ======== TEMA ESCURO / CLARO ========

    // Toggle para modo escuro/claro
    const themeToggle = document.getElementById('themeToggle');
    if (themeToggle) {
        // Verificar preferência salva
        const savedTheme = localStorage.getItem('theme');
        if (savedTheme === 'dark') {
            document.body.classList.add('dark-mode');
            themeToggle.checked = true;
            applyPlotlyTheme();
        }

        themeToggle.addEventListener('change', function() {
            if (this.checked) {
                document.body.classList.add('dark-mode');
                localStorage.setItem('theme', 'dark');
            } else {
                document.body.classList.remove('dark-mode');
                localStorage.setItem('theme', 'light');
            }

            // Atualizar gráficos para o novo tema
            if (typeof Plotly !== 'undefined') {
                applyPlotlyTheme();
            }
        });
    }

    // ======== MELHORIAS DE ACESSIBILIDADE ========

    // Adicionar atributos ARIA para melhorar acessibilidade
    document.querySelectorAll('button:not([aria-label])').forEach(button => {
        if (button.textContent.trim()) {
            button.setAttribute('aria-label', button.textContent.trim());
        } else if (button.querySelector('i')) {
            const iconClass = button.querySelector('i').className;
            if (iconClass.includes('search')) {
                button.setAttribute('aria-label', 'Pesquisar');
            } else if (iconClass.includes('download')) {
                button.setAttribute('aria-label', 'Baixar');
            } else if (iconClass.includes('print')) {
                button.setAttribute('aria-label', 'Imprimir');
            } else {
                button.setAttribute('aria-label', 'Botão');
            }
        }
    });

    // ======== NOTIFICAÇÕES DO SISTEMA ========

    // Função para mostrar notificações
    window.showNotification = function(message, type = 'info', duration = 5000) {
        const notificationArea = document.getElementById('notificationArea');
        if (!notificationArea) {
            const newNotificationArea = document.createElement('div');
            newNotificationArea.id = 'notificationArea';
            newNotificationArea.style.position = 'fixed';
            newNotificationArea.style.top = '20px';
            newNotificationArea.style.right = '20px';
            newNotificationArea.style.zIndex = '9999';
            document.body.appendChild(newNotificationArea);
        }

        const notification = document.createElement('div');
        notification.className = `toast bg-${type}`;
        notification.setAttribute('role', 'alert');
        notification.setAttribute('aria-live', 'assertive');
        notification.setAttribute('aria-atomic', 'true');

        notification.innerHTML = `
            <div class="toast-header">
                <strong class="me-auto">Dashboard SO</strong>
                <small>Agora</small>
                <button type="button" class="btn-close" data-bs-dismiss="toast" aria-label="Fechar"></button>
            </div>
            <div class="toast-body text-white">
                ${message}
            </div>
        `;

        document.getElementById('notificationArea').appendChild(notification);

        if (typeof bootstrap !== 'undefined') {
            const toast = new bootstrap.Toast(notification, {
                autohide: true,
                delay: duration
            });
            toast.show();

            // Remover após fechar
            notification.addEventListener('hidden.bs.toast', function() {
                notification.remove();
            });
        } else {
            // Fallback se o Bootstrap não estiver disponível
            setTimeout(() => {
                notification.remove();
            }, duration);
        }
    };

    // ======== MELHORIAS DE DESEMPENHO ========

    // Lazy loading para imagens
    document.querySelectorAll('img:not([loading])').forEach(img => {
        img.setAttribute('loading', 'lazy');
    });

    // Debounce para eventos de redimensionamento
    function debounce(func, wait) {
        let timeout;
        return function() {
            const context = this;
            const args = arguments;
            clearTimeout(timeout);
            timeout = setTimeout(() => func.apply(context, args), wait);
        };
    }

    // Aplicar debounce ao redimensionamento de gráficos
    const debouncedResize = debounce(function() {
        if (typeof Plotly !== 'undefined') {
            const charts = document.querySelectorAll('[id$="-chart"]');
            charts.forEach(function(chart) {
                if (chart && chart.id) {
                    Plotly.relayout(chart.id, {
                        'width': chart.offsetWidth,
                        'height': chart.offsetHeight
                    });
                }
            });
        }
    }, 250);

    window.addEventListener('resize', debouncedResize);

    // ======== INICIALIZAÇÃO FINAL ========

    // Mostrar notificação de boas-vindas (opcional)
    setTimeout(() => {
        if (window.showNotification) {
            window.showNotification('Dashboard atualizado com sucesso!', 'success', 3000);
        }
    }, 1000);

    console.log('Inicialização completa do dashboard!');
});
