var buy_price
var sell_price
var i;
var buy_price_map = new Map()
var sell_price_map = new Map()
var interval_var;
var table = document.getElementById("my_table");


function sortTable(n) {
    var table, rows, switching, i, x, y, shouldSwitch, dir, switchcount = 0;
    table = document.getElementById("my_table");
    switching = true;
    // Set the sorting direction to ascending:
    dir = "desc";
    // Set whether to sort by number
    sortByNumber = false
    if ((n==4) || (n==5)){
        sortByNumber = true
    }
    /* Make a loop that will continue until
    no switching has been done: */
    while (switching) {
        // Start by saying: no switching is done:
        switching = false;
        rows = table.rows;
        /* Loop through all table rows (except the
        first, which contains table headers): */
        for (i = 1; i < (rows.length - 1); i++) {
        // Start by saying there should be no switching:
            shouldSwitch = false;
            /* Get the two elements you want to compare,
            one from current row and one from the next: */
            x = rows[i].getElementsByTagName("TD")[n];
            y = rows[i + 1].getElementsByTagName("TD")[n];
            /* Check if the two rows should switch place,
            based on the direction, asc or desc: */
            if (dir == "asc") {
                if (sortByNumber == false )
                {
                    if (x.innerHTML.toLowerCase() < y.innerHTML.toLowerCase()) {
                        // If so, mark as a switch and break the loop:
                        shouldSwitch = true;
                        break;
                    }
                }
                else
                {
                    if (Number(x.innerHTML) < Number(y.innerHTML)) {
                        shouldSwitch = true;
                        break;
                    }
                }
            }
            else if (dir == "desc") {
                if (sortByNumber == false )
                {
                    if (x.innerHTML.toLowerCase() > y.innerHTML.toLowerCase()) {
                    // If so, mark as a switch and break the loop:
                    shouldSwitch = true;
                    break;
                    }
                }
                else
                {
                    if (Number(x.innerHTML) < Number(y.innerHTML)) {
                    shouldSwitch = true;
                    break;
                    }
                }
            }
        }
        if (shouldSwitch) {
            /* If a switch has been marked, make the switch
            and mark that a switch has been done: */
            rows[i].parentNode.insertBefore(rows[i + 1], rows[i]);
            switching = true;
            // Each time a switch is done, increase this count by 1:
            switchcount ++;
        }
        else
        {
            /* If no switching has been done AND the direction is "asc",
            set the direction to "desc" and run the while loop again. */
            if (switchcount == 0 && dir == "asc") {
                dir = "desc";
                switching = true;
            }
        }
    }
}

function add_new_row_to_table(stock_symbol,eps_array,net_income_array,sales_array, volume_change, price_change){

    var row = table.insertRow(1);
    row.id = stock_symbol

    // Insert new cells (<td> elements) at the 1st and 2nd position of the "new" <tr> element:
    var cell1 = row.insertCell(0);
    var cell2 = row.insertCell(1);
    var cell3 = row.insertCell(2);
    var cell4 = row.insertCell(3);
    var cell5 = row.insertCell(4);
    var cell6 = row.insertCell(5);
    // Add some text to the new cells:
    cell1.innerHTML = stock_symbol;
    cell2.innerHTML = eps_array;
    cell3.innerHTML = net_income_array;
    cell4.innerHTML = sales_array;
    cell5.innerHTML = volume_change;
    cell6.innerHTML = price_change;

}


function update_color_of_cell(cell, price_change){

    if (price_change > 0){
        cell.innerHTML.style.backgroundColor = "green";
    }
    else{
        cell.innerHTML.style.backgroundColor = "red";
    }


}


function update_key_of_table(stock_symbol,eps_array,net_income_array,sales_array, volume_change, price_change){

    row = document.getElementById(stock_symbol);

    row.cells[1].innerHTML = eps_array;
    row.cells[2].innerHTML = net_income_array;
    row.cells[3].innerHTML = sales_array;
    row.cells[4].innerHTML = volume_change;
    row.cells[5].innerHTML = price_change;
    update_color_of_cell(row.cells[5],price_change)

}


function get_volume_update(){

    const Http = new XMLHttpRequest();
    const url='http://127.0.0.1:8000/volume_update/';
    Http.open("GET", url,true);

    Http.send();
    Http.addEventListener("readystatechange", function() {
        //The operation is complete
        if (this.readyState === 4) {
            // http response success
            if (Http.status === 200) {
                stock_dict = Http.responseText;
                var stock_dict_parsed = JSON.parse(stock_dict);
                for (var key in stock_dict_parsed){
                    // stock is in the table therefore update the values
                    if (document.getElementById(key) != null){
                        update_key_of_table( key, stock_dict_parsed[key][0], stock_dict_parsed[key][1], stock_dict_parsed[key][2], stock_dict_parsed[key][3],stock_dict_parsed[key][4],stock_dict_parsed[key][5]);
                    }
                    // stock is not in the table therefore add new row
                    else{
                        add_new_row_to_table( key, stock_dict_parsed[key][0], stock_dict_parsed[key][1], stock_dict_parsed[key][2], stock_dict_parsed[key][3],stock_dict_parsed[key][4],stock_dict_parsed[key][5]);
                    }
                }
            }
        }
    });
};

// utility function to get get_volume_update to run first and then every interval getting an update
function setIntervalAndExecute(fn, t) {
    fn();
    return(setInterval(fn, t));
}

// running get_volume_update every refresh time.
let refresh_time = 20000
setIntervalAndExecute(get_volume_update, refresh_time);
