    document.addEventListener("DOMContentLoaded", function () {
        var rowsPerPage = 10;
        var table = document.getElementById("table");
        var tbody = table.getElementsByTagName("tbody")[0];
        var rows = Array.from(tbody.getElementsByTagName("tr"));
        var pagination = document.querySelector(".pagination");
        var currentPage = 1;

        function displayPage(page, rowsToShow) {
            var start = (page - 1) * rowsPerPage;
            var end = start + rowsPerPage;
            rows.forEach(row => row.style.display = "none");
            rowsToShow.slice(start, end).forEach(row => row.style.display = "");
        }

        function setupPagination(rowsToShow) {
            pagination.innerHTML = '';
            var pagesCount = Math.ceil(rowsToShow.length / rowsPerPage);

            // Previous page button
            var prevPageItem = document.createElement("li");
            prevPageItem.className = "page-item";
            var prevPageLink = document.createElement("a");
            prevPageLink.className = "page-link";
            prevPageLink.href = "#";
            prevPageLink.innerText = "Previous";
            prevPageItem.appendChild(prevPageLink);
            pagination.appendChild(prevPageItem);

            // Page number buttons
            for (var i = 1; i <= pagesCount; i++) {
                var pageItem = document.createElement("li");
                pageItem.className = "page-item";
                var pageLink = document.createElement("a");
                pageLink.className = "page-link";
                pageLink.href = "#";
                pageLink.innerText = i;
                pageItem.appendChild(pageLink);
                pagination.appendChild(pageItem);

                pageLink.addEventListener("click", function (e) {
                    e.preventDefault();
                    currentPage = parseInt(this.innerText);
                    displayPage(currentPage, rowsToShow);
                });
            }

            // Next page button
            var nextPageItem = document.createElement("li");
            nextPageItem.className = "page-item";
            var nextPageLink = document.createElement("a");
            nextPageLink.className = "page-link";
            nextPageLink.href = "#";
            nextPageLink.innerText = "Next";
            nextPageItem.appendChild(nextPageLink);
            pagination.appendChild(nextPageItem);

            prevPageLink.addEventListener("click", function (e) {
                e.preventDefault();
                if (currentPage > 1) {
                    displayPage(--currentPage, rowsToShow);
                }
            });

            nextPageLink.addEventListener("click", function (e) {
                e.preventDefault();
                if (currentPage < pagesCount) {
                    displayPage(++currentPage, rowsToShow);
                }
            });

            displayPage(1, rowsToShow); // Display the first page
        }

        function updateSearchAndPagination() {
            var filter = document.getElementById("search").value;
            var filteredRows = rows.filter(row => row.textContent.indexOf(filter) > -1);
            currentPage = 1;
            setupPagination(filteredRows);
            
            // Save the search value to localStorage
            localStorage.setItem("searchValue", filter);
        }

        // Function to restore search value after page refresh
        window.onload = function () {
            var savedSearchValue = localStorage.getItem("searchValue");
            if (savedSearchValue) {
                document.getElementById("search").value = savedSearchValue;
                updateSearchAndPagination(); // Perform search with the saved value on page load
            }
        };

        document.getElementById("search").addEventListener("keyup", updateSearchAndPagination);

        setupPagination(rows); // Initial setup with all rows
    });
