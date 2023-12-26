document.addEventListener('DOMContentLoaded', function() {
    let preferredView = localStorage.getItem('preferredView');

    // Asegúrate de que estas rutas coincidan exactamente con la ubicación de tus archivos HTML
    const cardsPath = '/stacks-cards';
    const tablePath = '/stacks-list';

    if (preferredView === 'table' && !window.location.href.endsWith(tablePath)) {
        window.location.href = tablePath;
    } else if (preferredView === 'cards' && !window.location.href.endsWith(cardsPath)) {
        window.location.href = cardsPath;
    }
});


function changeView(view) {
    localStorage.setItem('preferredView', view);
    if (view === 'table') {
        window.location.href = '/stacks-list';
    } else {
        window.location.href = '/stacks-cards';
    }
}
