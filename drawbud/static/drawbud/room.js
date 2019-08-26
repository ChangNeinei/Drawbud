var ctx;
var isDragging = false;
var timerstart = false;
var countdown;
var socket;
var lobby_socket;


function displayMessage(message) {
    var errorElement = document.getElementById("message");
    errorElement.innerHTML = message;
}

function displayWord(word, isDrawer) {
  if(isDrawer) {
    
    $('#word_section').append(
        '<button id="word_button" type="button" class="btn btn-warning" data-toggle="popover" data-content="' + 
        word + '">Get my word</button>'
    );
    $('[data-toggle="popover"]').popover();
  }
  else{
    if ($('#word_section').length > 0) {
      $('[data-toggle="popover"]').popover('hide');
      $('#word_button').remove();

    }
  }
}

function canvasEvent(e) {
  var type = e.handleObj.type;

  // for getting offsets after scrolling the windows
  var offset = $(this)[0].getBoundingClientRect();
  var x = parseInt(e.clientX - offset.left) / $(this).width();
  var y = parseInt(e.clientY - offset.top) / $(this).height();

  draw(x, y, type);

  var data = new Object();
  data.x = x;
  data.y = y;
  data.type = type;
  socket.send(JSON.stringify(data));
}

function answerEvent(e) {
  var message = { 
      ans: $('#ans-message-input').val(),
      player: userName.player
  }
  
  socket.send(JSON.stringify(message));
  
  var param = "room_name=" + roomName + "&ans=" + $('#ans-message-input').val();
  var req = new XMLHttpRequest();
  req.open("GET", "/checkans" + "?" + param, true);
  req.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
  req.send(null);
  req.onreadystatechange=function(){
    if(req.readyState == 4 && req.status == 200){
      if(req.responseText == 'correct') {
        // inform other correct
        var correct_message = {
          status: 'correct',
          guesser: userName.player
        }
        socket.send(JSON.stringify(correct_message));
      }
    }
  }

  return false;
}

function enableCanvas() {
  // add event listener on the canvas
  $("canvas").on('mousedown mouseup mousemove', canvasEvent);
}

function disableCanvas() {
  // remove event listener on the canvas
  $("canvas").off('mousedown mouseup mousemove', canvasEvent);
}

function enableAnswer() {
  // Enable submit button
  $('#ans-message-input').prop('disabled', false);
  $('#ans-message-submit').prop('disabled', false);
 
  // Answering 
  $('#ans-form').on('submit', answerEvent);
}

function disableAnswer() {
  // disable submit button
  $('#ans-message-input').prop('disabled', true);
  $('#ans-message-submit').prop('disabled', true);
 
  // Answering 
  $('#ans-form').off('submit', answerEvent);
}

function startGame(button) {

  // the mimimum players is 2
  if ($("#ans-log tbody").children().length <= 1) {
    window.alert("The minimum number of players for the game is two.");
    return;
  }

  getVoc();

  var start_message = {
    status: 'start',
    drawer: owner,
    word: voc
  }
  console.log(start_message);
  socket.send(JSON.stringify(start_message));

  // remove the room from the lobby
  var start_room = {
    start_room: roomName
  }
  lobby_socket.send(JSON.stringify(start_room));
  
  // update the room status
  var req = new XMLHttpRequest();
  req.open("POST", "/startroom/" + roomName, true);
  req.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
  req.send("&csrfmiddlewaretoken=" + getCSRFToken());
  req.onreadystatechange=function(){
    if(req.readyState == 4 && req.status == 200){
      console.log("start game.");
    }
  }

  button.parentNode.removeChild(button);
}

function showPass() {
  if($('#pass_button').length > 0){
    $('#pass_button').css("display", "inline-block");
  }
  else{
    $('#heading-text').append(
      '<button id="pass_button" type="button" class="btn btn-primary btn-lg" onclick="sendPass()">Pass</button>'
    )
  }
}

function hidePass() {
  $('#pass_button').css("display", "none");
}

function setDrawingStyle() {
  ctx.fillStyle = "solid";
  ctx.strokeStyle = "#bada55";
  ctx.lineWidth = "3";
  ctx.lineCap = "round";
}

function draw(x, y, type) {
  var w = $("canvas").width();
  var h = $("canvas").height();

  if (type == "mousedown") {
    isDragging = true;
    
    ctx.beginPath();
    ctx.moveTo(Math.round(x*w), Math.round(y*h));
  }
  else if (type == "mousemove" && isDragging) {
    ctx.lineTo(Math.round(x*w), Math.round(y*h));
    ctx.stroke();
  }
  else {
    isDragging = false;
    ctx.closePath();
  }
}

function getVoc() {
  var req = new XMLHttpRequest();
  req.open("POST", "/getvoc/" + roomName, false);
  req.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
  req.send("&csrfmiddlewaretoken=" + getCSRFToken());
  if(req.status == 200){
    console.log("get new word.");
    voc = req.responseText;
  }
}

function nextDrawer() {
  drawerID = (drawerID + 1) % $('#ans-log tbody').children().length;
  var next_drawer = $("#ans-log tbody").find("tr:eq(" + drawerID.toString() + ")")
    .find("td:eq(0)").text().trim();
  
  // get the next word
  getVoc();

  // inform all the players who is the next drawer
  var message = {
    status : "next_drawer",
    drawer : next_drawer,
    word: voc
  }
  socket.send(JSON.stringify(message));
}

function sendPass() {
  var pass_message = {
    status: 'pass',
  }
  socket.send(JSON.stringify(pass_message));
}

function nextRound() {
  isDragging = false;
  // select the next player
  $("#player_list_" + curr_drawer).find("td:eq(0)").css("color", "black");
  $("#player_list_" + curr_drawer).find("td:eq(0)").find("div").find("span:eq(1)").remove();
              
  if(userName.player === owner) {
    nextDrawer(); // to next player
  }
}

function getCSRFToken() {
    var cookies = document.cookie.split(";");
    for (var i = 0; i < cookies.length; i++) {
        c = cookies[i].trim();
        if (c.startsWith("csrftoken=")) {
            return c.substring("csrftoken=".length, c.length);
        }
    }
    return "unknown";
}

function checkRefresh() {
  if (document.location.hash === '#visited'){
    return true;
  }
  else {
    document.location.hash = 'visited';
    return false;
  }
}

function leavePage(){
  if(!checkRefresh()){
    
    var delete_player = {
      delete_player: userName.player
    }
    socket.send(JSON.stringify(delete_player));

    
    var fd = new FormData();
    fd.append('csrfmiddlewaretoken', getCSRFToken());
    navigator.sendBeacon('/remove/' + userName.player, fd);

    // update the number of players at lobby
    var room_to_leave = {
      leave_room: roomName,
    }
    lobby_socket.send(JSON.stringify(room_to_leave));
   
  }
  // leave the page and close the socket
  socket.close();
  lobby_socket.close();
  // avoid prompt
  return undefined;
}

function saveImage() {
  // Convert canvas image to URL format (base64)
  var download = document.getElementById("download");
  var image = document.getElementById("myCanvas").toDataURL("image/png")
                    .replace("image/png", "image/octet-stream");
  download.setAttribute("href", image);
}

window.onload = function() {


  // Create a socket
  socket = new WebSocket("ws://" + window.location.host + "/ws/room/" + roomName);

  // To notify the lobby that a user leave
  lobby_socket = new WebSocket("ws://" + window.location.host + "/ws/lobby/");
  lobby_socket.onerror = function(error) {
    displayMessage(error);
  }
  lobby_socket.onclose = function(event){}
  lobby_socket.onmessage = function(event){}

  socket.onerror = function(error) {
    displayMessage(error);
  }


  // Show a connected message when the WebSocket is opened.
  socket.onopen = function(event) {
      
      // send the new player info to the server using websocket
      socket.send(JSON.stringify(userName));
  }

  // Show a disconnected message when the WebSocket is closed.
  socket.onclose = function(event) {
  }

  // Handle the event from the server
  socket.onmessage = function(event) {
        var response = JSON.parse(event.data);
        if(response.hasOwnProperty('x') 
           && response.hasOwnProperty('y') 
           && response.hasOwnProperty('type')){
          draw(response.x, response.y, response.type);
        }
        else if(response.hasOwnProperty('player')){
          // not append to the list if the player already there
          if($('#ans-log').children(":contains('" + response.player + "')").length === 0){
            var number = $('#ans-log tbody').children().length + 1;
            $('#ans-log').append('<tr id=player_list_' + response.player + '>'
              + '<td>' + '<div class="img_cont">' 
              + '<img src="../static/drawbud/images/' + number.toString() +'.png" class="rounded-circle user_img">'
              + '<span class="title"> ' + response.player + '</span>'
              + '</td>'
              + '</tr>');
          }
        }
        else if(response.hasOwnProperty('ans')){
          if (document.getElementById("id_ans_" + response.player_id) == null) {
            $('#player_list_' + response.player_id).append( '<td id=id_ans_' + response.player_id + '>' 
              + '<div class="img_cont">'
              + '<h5><span class="badge badge-pill badge-warning">' + response.ans + '</span></h5>' 
              + '</div>'
              + '</td>');
          }
          else {
            $('#id_ans_' + response.player_id).replaceWith('<td id=id_ans_' + response.player_id + '>' 
              + '<div class="img_cont">'
              + '<h5><span class="badge badge-pill badge-warning">' + response.ans + '</span></h5>' 
              + '</div>'
              + '</td>');
          }
        }
        else if(response.hasOwnProperty('delete_player')){
          $('#player_list_'+ response.delete_player).remove();
          // if the owner leave the room, redirect to the lobby
          if (response.delete_player === owner) {
            window.alert("The owner left the room! Redirect to the lobby...");
            window.location.replace("http://" + window.location.host + "/leave_to_lobby/" + userName.player);
          }
          else if (start && $('#ans-log tbody').children().length <= 1) {
            window.alert("The minimum number of players is 2! Redirect to the lobby...");
            window.location.replace("http://" + window.location.host + "/leave_to_lobby/" + userName.player);
          }
          // the current drawer leave
          else if (response.delete_player === curr_drawer && userName.player === owner) {
            nextDrawer();
          }
        }
        else if(response.hasOwnProperty('status')){
          if (response.status === 'correct'){
            // inform others that someone got the right answer
            if (response.guesser === userName.player) {
              $("#success").text("You got the correct answer!").fadeIn(300).delay(1500).fadeOut(400);
            } else {
              $("#success").text(response.guesser + " got the correct answer!").fadeIn(300).delay(1500).fadeOut(400);
            }
            if (userName.player === curr_drawer) {
              
              var dataURL = document.getElementById("myCanvas").toDataURL()
              console.log(voc);
              
              $.ajax({
                type: "POST",
                url: '/uploadimage/',
                data: { 
                  imgBase64: dataURL,
                  csrfmiddlewaretoken: getCSRFToken(),
                  word: voc,
                }
              }).done(function(o) {
                console.log('saved');
              });
            }
            // reset the game
            nextRound();
          }
          else if (response.status === 'pass') {
            nextRound();
          }
          else {
            //let the player know the game start?!
            if (response.status === 'start') {
              start = true;
              if (userName.player !== curr_drawer) {
                window.alert("The game has started!");
              }
            }
            // change drawer
            // and also highlight the name of drawers
            curr_drawer = response.drawer;
            voc = response.word;
            // clean the canvas
            var canvas = $("#myCanvas");
            ctx.clearRect(0, 0, canvas.width(), canvas.height());
            // clean the ans table
            $("#ans-log tbody tr").each(function() {
              if ($(this).children().length == 2) {
                $(this).children().eq(1).text("");
              }
            });

            $("#player_list_" + curr_drawer).find("td:eq(0)").css("color", "red");
            $("#player_list_" + curr_drawer).find("td:eq(0)").find("div").append(
              '<span class="title">' + "is  drawing..." + '</span>' 
              );
            if (curr_drawer === userName.player){
              displayWord(voc, true);
              showPass();
              enableCanvas();
              disableAnswer();
            }
            else{
              displayWord(voc, false);
              hidePass();
              disableCanvas();
              enableAnswer();
            }
          }
        }
        else{
          displayMessage("Missing Property!");
        }
  }

  // Exit the room 1. click other button 2. close the window unload

  window.onbeforeunload = leavePage;
  

  
  var parent = $("#myCanvas").parent();
  
  // set canvas size
  $("#myCanvas")
    .attr("width", parent.width())
    .attr("height", 0.4 * $(window).height());

  ctx = $("#myCanvas")[0].getContext("2d");
  setDrawingStyle();
  


  
  // event handler for resizing the window
  $(window).resize(function(){

    var canvas = $("#myCanvas");

    // copy the original image to a temp canvas
    var tempCanvas = document.createElement('canvas');
    tempCanvas.width = canvas[0].width;
    tempCanvas.height = canvas[0].height;
    tmpCtx = tempCanvas.getContext('2d');
    tmpCtx.drawImage(canvas[0], 0, 0);
    

    canvas
      .css("width", '100%')
      .attr("width", parent.width())
      .attr("height", 0.4 * $(this).height());
    
    ctx = canvas[0].getContext("2d");

    setDrawingStyle();
    // paste the image
    ctx.drawImage(tempCanvas, 0, 0, tempCanvas.width, tempCanvas.height, 0, 0, 
                  canvas[0].width, canvas[0].height);
  });
  
}


