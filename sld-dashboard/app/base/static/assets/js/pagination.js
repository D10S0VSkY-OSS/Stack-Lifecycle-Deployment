$(document).ready(function(){
  var rowsPerPage = 20; // Valor inicial
  var rows = $('#myTable tr');
  var filteredRows = rows; // Inicialmente, todas las filas son el conjunto filtrado
  var pagesCount;
  var currentPage = 1;

  function displayPage(page) {
      var start = (page - 1) * rowsPerPage;
      var end = start + rowsPerPage;
      rows.hide();
      filteredRows.slice(start, end).show();
  }

  function setupPagination() {
      pagesCount = Math.ceil(filteredRows.length / rowsPerPage);
      $('.pagination .number-page').remove(); // Remove old page numbers
      for (var i = 1; i <= pagesCount; i++) {
          $('<li class="page-item number-page"><a class="page-link" href="#">' + i + '</a></li>')
              .insertBefore("#next-page")
              .on('click', function(e) {
                  e.preventDefault();
                  currentPage = parseInt($(this).text());
                  displayPage(currentPage);
                  $(".pagination .number-page").removeClass('active');
                  $(this).addClass('active');
              });
      }
      displayPage(1);
  }


  // Existing search functionality
  $("#myInput").on("keyup", function() {
      var value = $(this).val().toLowerCase();
      filteredRows = rows.filter(function() {
          return $(this).text().toLowerCase().indexOf(value) > -1;
      });
      currentPage = 1;
      setupPagination();
  });

  // Existing dropdown functionality
  $(".dropdown-menu a").on("click", function(e) {
      e.preventDefault();
      var selectedValue = $(this).text().trim();
      rowsPerPage = selectedValue.toLowerCase() === 'all' ? rows.length : parseInt(selectedValue);
      currentPage = 1; // Reset to first page
      setupPagination();
  });

  // Initial setup
  setupPagination();

  // Previous and Next button logic
  $("#previous-page").on('click', function(e) {
      e.preventDefault();
      if (currentPage > 1) {
          currentPage--;
          displayPage(currentPage);
      }
  });

  $("#next-page").on('click', function(e) {
      e.preventDefault();
      if (currentPage < pagesCount) {
          currentPage++;
          displayPage(currentPage);
      }
  });
});
d