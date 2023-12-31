// Function to perform search
function search() {
    var input, filter, table, tr, td, i, txtValue;
    input = document.getElementById("myInput");
    filter = input.value; 
    table = document.getElementById("table");
    tr = table.getElementsByTagName("tr");

    // Loop through all table rows, and hide those who don't match the search query
    for (i = 0; i < tr.length; i++) {
        td = tr[i].getElementsByTagName("td")[1]; // Cambia el índice para adaptarse a la columna que deseas buscar
        if (td) {
            txtValue = td.textContent || td.innerText;
            if (txtValue.includes(filter)) {
                tr[i].style.display = "";
            } else {
                tr[i].style.display = "none";
            }
        }
    }

    // Save the search value to localStorage
    localStorage.setItem("searchValue", filter);
}

// Function to restore search value after page refresh
window.onload = function () {
    var savedSearchValue = localStorage.getItem("searchValue");
    if (savedSearchValue) {
        document.getElementById("myInput").value = savedSearchValue;
        search(); // Realiza la búsqueda con el valor guardado al cargar la página
    }
};