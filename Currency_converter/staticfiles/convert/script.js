function highlight_highest_lowest() {
// Find the cell with the highest exchange rate
    let numColumns = document.getElementById("myTable").rows[0].cells.length;
    for (let i = 1; i < numColumns; i++) {
        // Find the cell with the highest exchange rate for this column
        let maxRate = 0;
        let maxRateCell = null;
        let minRate = Number.MAX_VALUE;
        let minRateCell = null;
        let rateCells = document.getElementsByClassName("rate");
        for (let j = i; j < rateCells.length; j += 1) {
            if ((j-i) % (numColumns-1) === 0) {
                let rateValue = parseFloat(rateCells[j].getAttribute("value"));
                if (rateValue > maxRate) {
                    maxRate = rateValue;
                    maxRateCell = rateCells[j];
                }
                if (rateValue < minRate) {
                minRate = rateValue;
                minRateCell = rateCells[j];
                }
            }
        }

        // Add a CSS class to the cell with the highest and lowest exchange rate for this column
        maxRateCell.classList.add("highest");
        minRateCell.classList.add("lowest");
    }
}

function highlight_highest_lowest_currency_page() {
// Find the cell with the highest exchange rate
    var rate_cells = document.querySelectorAll('table#myTable tbody td.rate:nth-child(2)');

    // Initialize variables to store the highest rates and their respective cells
    var highest_rate = -Infinity;
    var highest_cells = [];

    // Loop through all the rate cells and find the highest rates
    for (var i = 0; i < rate_cells.length; i++) {
      var rate = parseFloat(rate_cells[i].getAttribute('value'));
      if (rate > highest_rate) {
        highest_rate = rate;
        highest_cells = [rate_cells[i]];
      } else if (rate === highest_rate) {
        highest_cells.push(rate_cells[i]);
      }
    }

    // Add a class to highlight all the cells with the highest rate
    for (var i = 0; i < highest_cells.length; i++) {
      highest_cells[i].classList.add('highest');
    }
  }

  // Add an event listener to the window object to call the function when the page finishes loading
  window.addEventListener('load', function() {
    highlight_highest_lowest();
  });
