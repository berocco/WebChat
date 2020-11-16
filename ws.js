var server = 'ws://localhost:8080/';

function zPad(n) {
    if (n < 10) return '0' + n;
    else return n;
}

function timestamp() {
    var d = new Date();
    return zPad(d.getHours()) + ':' + zPad(d.getMinutes()) + ':' + zPad(d.getSeconds());
}

function write_to_mbox(message) {
    var mt = message.mt;
    var line = '[' + timestamp() + '] ' + message.data + '<br>';
    if (mt === "serv"){
        var line = line.fontcolor('green')
    }
    else if (mt === "pm"){
        var line = line.fontcolor('blue')
    }
    $('#messages').append(line);
}

$(document).ready(function() {
    var socket = new WebSocket(server);
    var clients = [];
    $('#name').focus();
    
    socket.onerror = function(error) {
        console.log('WebSocket Error: ' + error);
    };

    socket.onclose = function(event) {
        write_to_mbox({'mt':'serv', 'data':'Desconectado do Web Chat'});
    };

    socket.onmessage = function(event) {
        var recv = JSON.parse(event.data);
        console.log(recv);
        if (recv.mt === 'clients'){
            if (!recv.data){
                $('#connected').text('Sem usuários conectados');
            }
            else{
                clients = recv.data.split(', ')
                $('#connected').text(''.concat('Usuários conectados: ', recv.data));
            };    
        }
        else{
            write_to_mbox(recv)
        };
    };

    $('#message-form').submit(function() {
        socket.send($('#message').val());
        $('#message').val('');
        return false;
    });

    $('#connect-form').submit(function() {
        var name = $('#name').val().trim();
        if (clients.includes(name)){
            alert("Nome já utilizado, escolha outro")
        }
        else if (name.includes(' ')){
            alert("Não são permitidos espaços no nome de usuário")
        }
        else{
            socket.send(name);
            
            $('#jumbotron').hide();
            $('#ttl').text("Web Chat");

            write_to_mbox({'mt':'serv', 'data':"Conectado ao chat!"});
            
            $('#message_wrapper').show();
            $('#message').focus();
        };
        return false;
    });
});
