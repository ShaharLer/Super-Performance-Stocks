var buy_price
var sell_price
var table = document.getElementById("my_table");
var i;
var buy_price_map = new Map() 
var sell_price_map = new Map() 


function Add_stock(){

    var stock_id = table.rows.length
    
    add_new_row_to_table(stock_id);
    
    elemt_id = document.getElementById('buy_input_'+stock_id)
    elemt_id.addEventListener("keyup", function(){
        buy_price_map.set(stock_id,this.value)
    });

    
    elemt_id2 = document.getElementById('sell_input_'+stock_id)
    elemt_id2.addEventListener("keyup", function(){
        sell_price_map.set(stock_id,this.value)

    }); 

}

function calculate_profit_or_loss(buy_price, sell_price){

    let change = 0
    let result_precentage = 0
    
    if (buy_price < sell_price){
        change = sell_price - buy_price
    }
    else{
        change = sell_price - buy_price
    } 

    result_precentage = (change / buy_price ) * 100

    return result_precentage 
}

function set_profit_loss_value(stock_id){
   
    var profit_loss = document.getElementById('profit_loss_'+stock_id)
    let buy_price  = buy_price_map.get(Number(stock_id))
    let sell_price  = sell_price_map.get(Number(stock_id))
    profit_loss.innerHTML = calculate_profit_or_loss(buy_price,sell_price)+'%' 

}


function disable_or_enable_inputs(stock_id, is_disable){
    document.getElementById('buy_input_'+stock_id).disabled = is_disable; 
    document.getElementById('sell_input_'+stock_id).disabled = is_disable; 
    document.getElementById('stock_name_input_'+stock_id).disabled = is_disable; 
    document.getElementById('stock_buy_date_input_'+stock_id).disabled = is_disable; 
    document.getElementById('stock_sell_date_input_'+stock_id).disabled = is_disable; 
}

function select_button(stock_id){  
  
    set_profit_loss_value(stock_id);
    disable_or_enable_inputs(stock_id, true)

}

function edit_button(stock_id){  
    disable_or_enable_inputs(stock_id, false)
}

function remove_button(btn){
    var row = btn.parentNode.parentNode;
    row.parentNode.removeChild(row);
}

function add_new_row_to_table(stock_id){
    var row = table.insertRow(-1);
    
    row.innerHTML = '<th scope="row"><input type="text" id="stock_name_input_'+stock_id+'" name = "input"></th>'+
    '<tr> \
    <td><input type="date"  id="stock_buy_date_input_'+stock_id+'" name="trip-start" value="2020-07-22" min="2018-01-01" max="2022-12-31"></td>\ \
    <td><input type="date" id="stock_sell_date_input_'+stock_id+'" name="trip-start" value="2020-07-22" min="2018-01-01" max="2022-12-31"></td>\  \
    <td ><input type="number"  step="0.01" id="buy_input_'+stock_id+'" name = "input"></td>\  \
    <td><input type="number"  step="0.01" id="sell_input_'+stock_id+'" name = "input"></td>\  \
    <td><button  onclick="select_button(\'' + stock_id + '\')"> click to set </button><br><button  onclick="remove_button(this)">Click to Remove </button> <br> <button  onclick="edit_button(\'' + stock_id + '\')">Click to Edit </button> <td id ="profit_loss_'+stock_id+'" > 0 </td> </tr>'
}






