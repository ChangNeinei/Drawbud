var room_socket;

function displayMessage(message) {
    var errorElement = document.getElementById("message");
    errorElement.innerHTML = message;
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

function joinClick(room_name) {
  // TODO even the database would not allow the same user to join the room
  // the websocket would send the message that the same user join and update the 
  // lobby
  var message = {
    room_name : room_name,
    curr_player_number : (parseInt($('#curr_num_' + room_name).text()) + 1).toString(),
    max_player_number : $('#max_num_' + room_name).text(),
  }
  room_socket.send(JSON.stringify(message));

  $('#join_' + room_name).submit();
}

window.onload = function() {
  // Create a socket
  room_socket = new WebSocket("ws://" + window.location.host + "/ws/lobby/");

  room_socket.onerror = function(error) {
    displayMessage(error);
  }

  // Show a connected message when the WebSocket is opened.
  room_socket.onopen = function(event) {

      //displayMessage("WebSocket Connected");
  }

  // Show a disconnected message when the WebSocket is closed.
  room_socket.onclose = function(event) {
      //displayMessage("WebSocket Disconnected");
  }

  $('#room_button').on('click', function(event) {
    // console.log(typeof JSON.stringify($('#room_name').val()));
    var roomname  = JSON.stringify($('#room_name').val());
    
    var room = roomname.substr(1, roomname.length - 2);
    
    var result = /^[A-Za-z0-9]+$/.test(room);
    console.log(result);
    if (room.indexOf(' ') >= 0) {
      alert("Room name can't contain space");
      return;
    }
    if (!result) {
      console.log("don't match");
      alert("Room name can only contain numbers and alphabets");
      return;
    }
    
    console.log("match");
    var message = {
    room_name : $('#room_name').val(),
    max_player_number : $('#max_player_number').val(),
    owner: user,
    description : $('#room_description').val(),
    }
    room_socket.send(JSON.stringify(message));
    $('#room_form').submit();
      
  });
  
  // Handle the event from the server
  room_socket.onmessage = function(event) {
    var response = JSON.parse(event.data);
    // create room
    //if (response.room_name.indexOf(' ') >= 0) {
      //console.log("In the function")
      // return;
    //}
    if(response.hasOwnProperty('owner')) {
       
      $('#room_row').append(
        '<div id="' + response.room_name + '"class="col-md-4">' +
          '<div class="card mb-4 shadow-sm">' +
            '<svg class="bd-placeholder-img card-img-top" width="100%" height="225">'+
            '<rect width="100%" height="100%" fill="#F4A460"/>'+
            '<text x="50%" y="50%" text-anchor="middle" fill="#eceeef" id="room_link">' + response.room_name + '</text>' +
            '<text x="50%" y="65%" text-anchor="middle" fill="#eceeef">Owner: ' + response.owner + '</text>'+
            '</svg>'+
            '<div class="card-body">'+
              '<p class="card-text">' + response.description +'</p>' + 
              '<div class="d-flex justify-content-between align-items-center">' +
                '<form id="join_' + response.room_name + '" action="/get_room/'+response.room_name + '" method="post">' +
                  '<button type="submit" class="btn btn-sm btn-outline-secondary" onclick="joinClick(\'' + response.room_name +'\')">'
                  + 'Join Room' +
                  '</button>' +
                  '<input type="hidden" name="csrfmiddlewaretoken" value=' + getCSRFToken() +'>'+
                '</form>' + 
                  '<small class="text-muted">People: </small>' +
                  '<small id="curr_num_'+ response.room_name + '" class="text-muted">1</small>' +
                  '<small class="text-muted">/</small>'+
                  '<small id="max_num_'+ response.room_name + '" class="text-muted">' + response.max_player_number + '</small>' +
              '</div>' +
            ' </div> ' +
          ' </div> ' +
        '</div>');
    }
    // increase the number of players
    else if (response.hasOwnProperty('curr_player_number')) {
      if(response.curr_player_number === response.max_player_number) {
        // hidden the room from the list
        if( $("#" + response.room_name).length > 0){
          $("#" + response.room_name).css("display", "none");
          //$("#" + response.room_name).remove();
        }
      }
      if ($("#curr_num_" + response.room_name).length > 0){
        // update the current number of participants
        $("#curr_num_" + response.room_name).text(response.curr_player_number);
      }
    }
    // decrease the number of players
    else if (response.hasOwnProperty('leave_room_name')) {
      var new_curr_num = parseInt($("#curr_num_" + response.leave_room_name).text()) - 1;
      if( new_curr_num === 0) {
        // remove the room from the list if no people in the room
        if( $("#" + response.leave_room_name).length > 0){
          $("#" + response.leave_room_name).remove();
        }
      }
      else if ($("#curr_num_" + response.leave_room_name).length > 0){
        $("#curr_num_" + response.leave_room_name).text(new_curr_num.toString());
        // display the hidden room
        if( $("#" + response.leave_room_name).length > 0){
          console.log("display the room");
          $("#" + response.leave_room_name).css("display", "block");
        }
      }
    }
    else if (response.hasOwnProperty('start_room')) {
      if( $("#" + response.start_room).length > 0){
        $("#" + response.start_room).remove();
      }
    }
  };
}
