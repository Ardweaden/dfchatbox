//INIT
var j = 0;
var autocompleting = 1;
var global_username = "Uporabnik";
var patientInfo_name, patientInfo_lastname, patientInfo_ehrid,patientInfo_patients,patientInfo_isDoctor;
var welcome_message = "Pozdravljeni, sem ThinkEHR robotski pomočnik! Za prijavo kliknite na ime na zgornjem levem robu pogovornega okenca.";
var greeting = true;
var wait_time_limit = 15000;
var current_timeout = false;
var response_type = "";

$(document).ready(function(){
    //localStorage.removeItem("sessionID");
    //session_isValid();
    var index = sessionStorage.getItem("index")
    if (isNaN(index)) {
        sessionStorage.setItem("index",0);
    }

    $("#socketchatbox-sendFileBtn").css("background","#9a969a");
    $(".arrow-right").css("border-left","25px solid #bcbabb");

    if (greeting) {
        welcome_bubble = '<div style="padding-bottom:13%;" class="socketchatbox-message-wrapper" id="Welcome_message"><div class="socketchatbox-message socketchatbox-message-others"><div class="socketchatbox-username">DialogFlow<span class="socketchatbox-messagetime"></span></div><span class="socketchatbox-messageBody socketchatbox-messageBody-others">' + welcome_message + '</span><br></div></div>';
        $(".socketchatbox-chatArea").append(welcome_bubble);
        saveElement(welcome_bubble);
    }

    j = 1;

    sessionStorage.setItem("current_word","");

    user_status = sessionStorage.getItem("logged-in");

    console.log("user status is: " + user_status);

    if (user_status == 1) {
        $("#login-logout").css("background-color","green");
        $("#socketchatbox-username").text(sessionStorage.getItem("username"));
        global_username = sessionStorage.getItem("username");
        patientInfo_name = sessionStorage.getItem("patientInfo_name");
        patientInfo_lastname = sessionStorage.getItem("patientInfo_lastname");
        patientInfo_ehrid = sessionStorage.getItem("patientInfo_ehrid");
        patientInfo_isDoctor = sessionStorage.getItem("patientInfo_isDoctor");
    }
    else {
        $("#login-logout").css("background-color","red");
        var url = window.location.href + "logout";
        $.post(url,function(response){console.log(response)});
    }
    //console.log("SESSION ID: " + localStorage.getItem("sessionID"));




    console.log("\npatientInfo_name: " + patientInfo_name + "\npatientInfo_lastname: " + patientInfo_lastname + "\npatientInfo_ehrid: " + patientInfo_ehrid + "\npatientInfo_isDoctor: " + patientInfo_isDoctor);
});

$(".socketchatbox-page").keydown(function(t){
    var message = $(".socketchatbox-inputMessage").val();

    if (message == "") {
        $("#socketchatbox-sendFileBtn").css("background","#9a969a");
        $(".arrow-right").css("border-left","25px solid #bcbabb");
    }
    if (!message.replace(/\s/g, '').length) {
        $("#socketchatbox-sendFileBtn").css("background","#9a969a");
        $(".arrow-right").css("border-left","25px solid #bcbabb");
    }
    else {
        $("#socketchatbox-sendFileBtn").css("background","#4DACFF");
        $(".arrow-right").css("border-left","25px solid #80DFFF");
    }
});


//EXTREMELY FANCY USER SESSION ID GENERATOR, MIGHT BE IMPROVED LATER
function UUSID() {
    return Math.floor(10000000*Math.random())
};

//SET SESSION ID
function set_sessionID() {
    var sessionID = UUSID();

    localStorage.setItem("sessionID",sessionID);
    localStorage.setItem("sessionStart",timestamp())
};

//UNIX TIMESTAMP
function timestamp() {
    var timestamp = new Date;
    return timestamp.getTime()/1000
};

//CHECK THE VALIDITY OF SESSION AND SET IT IF NOT VALID
function session_isValid() {
    var sessionTimeout = 900;

    var sessionID = localStorage.getItem("sessionID");
    var sessionStart = localStorage.getItem("sessionStart");

    var currentTime = timestamp();

    if (sessionID != null && sessionStart != null) {
        if ((currentTime - sessionStart) > sessionTimeout) {
            set_sessionID();
            return false
        }
        else {
            return true
        }
    }
    else {
        set_sessionID();
        return false
    }
};

/*//SET SESSION INDEX
$(document).ready(function(){
    if (sessionStorage.getItem("index") == null) {
        sessionStorage.setItem("index",0);
    }
});
*/
//RETURNS CURRENT TIME
function cur_date() {
    var n = new Date
        , date = "";

    date += " (" + ("0" + n.getHours()).slice(-2) + ":" + ("0" + n.getMinutes()).slice(-2) + ":" + ("0" + n.getSeconds()).slice(-2) + ")";
    return date
};

//ADDS ANIMATED BUBBLES WHEN USER IS TYPING
function typing(start,typer) {
    if (start) {
        $(".socketchatbox-chatArea").append('<div class="socketchatbox-message-wrapper" id="typing_wrapper"><div style="width:150px;height:20px;" class="socketchatbox-message socketchatbox-message-' + typer + '"><span style="width:100%;height:100%;" class="socketchatbox-messageBody socketchatbox-messageBody-' + typer + '"><div class="cssload-loader"><div></div><div></div><div></div><div></div><div></div></div></span></div></div>');
        document.getElementById("typing_wrapper").scrollIntoView({behavior: "smooth"});
    }
    else {
        $("#typing_wrapper").remove();
    }
};

//AUTOMATICALLY ENABLE INPUT FIELD IF RESPONSE TAKES TOO LONG
function auto_enable_input(time_limit) {
    console.log("It has been disabled");
    current_timeout = setTimeout(disable_input,time_limit,0);
    $("#typing_wrapper").remove();
    console.log("It has been enabled");
}


//DISABLES THE INPUT FIELD WHEN INPUT IS BEING PROCESSED
function disable_input(start) {
    if (start) {
        $("#inputField").prop('disabled', true);
        $("#socketchatbox-sendFileBtn").css("background","#9a969a");
        $(".arrow-right").css("border-left","25px solid #bcbabb");
        $(".socketchatbox-inputMessage").css("border","1px solid #9a969a");
        auto_enable_input(wait_time_limit);
    }
    else {
        $("#inputField").prop('disabled', false);
        $("#socketchatbox-sendFileBtn").css("background","#4DACFF");
        $(".arrow-right").css("border-left","25px solid #80DFFF");
        $(".socketchatbox-inputMessage").css("border","1px solid #4DACFF");
    }
};


//SAVES CONVERSATION TO SESSION STORAGE
function saveElement(element) {
        var index = sessionStorage.getItem("index");

        sessionStorage.setItem(index, element);
        sessionStorage.setItem("index", parseInt(index) + 1);
};

//RELOADS SAVED CONVERSATION
function reload_session_storage() {
    if (j == 0){
        var index = parseInt(sessionStorage.getItem("index"));

        if (index == 0) {
            return
        }

        for (var i = 0; i < index; i++) {
            var element = sessionStorage.getItem(i);
            $(".socketchatbox-chatArea").append(element)
        }

        parser = new DOMParser();
        element = parser.parseFromString(element, "text/xml");

        document.getElementById(element.firstChild.id).scrollIntoView({behavior: "instant"});

        j = Math.floor(index/2.0);

    }
    if (j == 1) {
        document.getElementById("Welcome_message").scrollIntoView({behavior: "instant"});
    }
};

//TAKES USER INPUT AND COMMUNICATES WITH DIALOGFLOW
function communicate(message,j){
    $("#showAllEntries").remove();
    
    disable_input(true);
    typing(1,"me");

    date = cur_date();

    if (typeof(message) == 'object'){
        var value = message[0];
        message = message[1];
        console.log("Value  ===  " + value + " which becomes message and is of type " + typeof(value));
        value = value.toString();
    }

    message = message.replace(/</g, "&lt;").replace(/>/g, "&gt;");

    //CHECKS FOR URLS IN THE QUERY
    ////////////////////////////////////////////////////////////////////////////////// CURRENTLY DISABLED URL CHECKING //////////////////////////////////////////////////////////////////////////////////////
    //$.post('/check_links', {'message':message}, function(response){

    //if (response != ""){
    ////////////////////////////////////////////////////////////////////////////////// CURRENTLY DISABLED URL CHECKING //////////////////////////////////////////////////////////////////////////////////////
    if (false){
        //APPEND THE URL TITLE AND IMAGE OF THE WEBSITE IF THERE ARE LINKS
        data = JSON.parse(response);
        static_string = "static/dfchatbox/img/" + data['image_name']

        typing(0,"me");

        var reply_me = '<div class="socketchatbox-message-wrapper" id="wrapper-me' + j + '"><div class="socketchatbox-message socketchatbox-message-me"><div class="socketchatbox-username">' + global_username + '<span class="socketchatbox-messagetime">' + date + '</span></div><span class="socketchatbox-messageBody socketchatbox-messageBody-me">' + message +  '</span><br><span class="socketchatbox-messageBody socketchatbox-messageBody-me"><a target="_blank" href="' + data['url'] + '">' + data['data'] + '</a><img src="' + static_string + '" style="width:100%;height:100%;"></span></div></div>';

        $(".socketchatbox-chatArea").append(reply_me);

        //SAVING TO SESSION STORAGE
        saveElement(reply_me);

        }

    else {
        //APPEND THE MESSAGE THERE ARE NO URLS 
        typing(0,"me");

        var reply_me = '<div class="socketchatbox-message-wrapper" id="wrapper-me' + j + '"><div class="socketchatbox-message socketchatbox-message-me"><div class="socketchatbox-username">' + global_username + '<span class="socketchatbox-messagetime">' + date + '</span></div><span class="socketchatbox-messageBody socketchatbox-messageBody-me">' + message +  '</span></div></div>';

        $(".socketchatbox-chatArea").append(reply_me);

        //SAVING TO SESSION STORAGE
        saveElement(reply_me);

    }

    document.getElementById("wrapper-me" + j).scrollIntoView({behavior: "smooth"});

    //DIALOFLOW RESPONSE

    typing(1,"others");

    if (value) {
        message = value;
    }

    //CHECKS SESSION
    session_isValid();
    var sessionID = localStorage.getItem("sessionID");
    localStorage.setItem("sessionStart", timestamp());

    //SENDS DATA TO DJANGO WHICH COMMUNICATES WITH DIALOFLOW
    $.post(window.location.href, {"message": message, "sessionID": sessionID, "name": patientInfo_name, "surname": patientInfo_lastname, "ehrid": patientInfo_ehrid},function(response){

        try {
            if (current_timeout != false) {
                clearTimeout(current_timeout);
            }
            //DIALOGFLOW RESPONSE CONTAINS DATA
            response = response.replace(/\n/g, "\\n");
            response = response.replace(/\r/g, "\\r");
            response = JSON.parse(response);

            if (response['data'] == "" || response['data'] == "[]") {
                throw "No data"
            }

            try {
                $("#URLiFrame").remove();
            }
            catch(err){}

            if (response['url']) {
                console.log("This is the url: ", response['url']);
                $("body").append('<iframe frameborder="0" style="overflow:hidden;height:100%;width:100%" id="URLiFrame" src="' + response['url'] + '" height="100%" width="100%"></iframe>')
            }

            typing(0,"others");

            //APPENDS TEXT RESPONSE
            console.log("TEXT RESPONSE ======> ",response);
            if (response_type == "entry") {
                console.log("Perhaps we shouldn't append")
            }
            var reply_others = '<div style="padding-bottom:1%;" class="socketchatbox-message-wrapper" id="wrapper-others' + j + '"><div class="socketchatbox-message socketchatbox-message-others"><div class="socketchatbox-username">DialogFlow<span class="socketchatbox-messagetime">' + date + '</span></div><span class="socketchatbox-messageBody socketchatbox-messageBody-others">' + response['text_answer'] + '</span><br></div></div>';

            $(".socketchatbox-chatArea").append(reply_others);

            saveElement(reply_others);

            //<span id="option_holder' + j + '" class="socketchatbox-messageBody socketchatbox-messageBody-me"></span>

            var i = 0;

            //*************************************************************************** USER OPTION BUTTONS ***********************************************************************************************
            // for (msg in response) {
            //     $(".socketchatbox-chatArea").append('<button class="choice_btn socketchatbox-messageBody socketchatbox-messageBody-me" id="btn' + i + j + '" type="button">' + response[i] + '</button>');
            //     i += 1;
            // }
            //*************************************************************************** USER OPTION BUTTONS ***********************************************************************************************

            console.log(response['data']);
            data = JSON.parse(response['data'].replace(/'/g, '"'));
            response_type = response['response_type'];

            if (response_type == "list") {
                //DATA IS LIST OF JSON OBJECTS
                console.log(data.length);
                console.log(data[0]);
                for (var k = 0; k < data.length; k++) {
                    var keys = Object.keys(data[k]);
                    var slo_keys = ["Datum","Ime","Vrednost"];

                    var oldDateFormat = new Date(data[k]['date']);
                    data[k]['date'] = oldDateFormat.toLocaleDateString();

                    var reply_others = '<div style="padding:0;" class="socketchatbox-message-wrapper" id="wrapper' + j + i + '"><div id="holder' + j + i + '" class="socketchatbox-message socketchatbox-message-others"><span style="margin-top:1%;margin-bottom:1%;width:200px;" id="data' + j + i + '" class="socketchatbox-messageBody socketchatbox-messageBody-others">'

                    for (var l = 0; l < keys.length; l++) {
                        reply_others += slo_keys[l] + ": " + data[k][keys[l]] + "<br>";
                        //$("#data" + j + i).append(keys[l] + ": " + data[k][keys[l]] + "<br>");
                    };

                    reply_others += '</span></div></div>';

                    $(".socketchatbox-chatArea").append(reply_others);

                    saveElement(reply_others);

                    i+=1;
                }
                disable_input(false);

                document.getElementById("wrapper" + j + (i-1)).scrollIntoView({behavior: "smooth"});

                $("#inputField").focus();
            }

            else if (response_type == "entry") {
                //DATA IS DICTIONARY
                console.log("entry");
                var keys = Object.keys(data);
                console.log("keys",keys);
                console.log(data);

                var disabled = localStorage.getItem("disableAllEntries");

                if (disabled == 0) {

                    reply_others = '<button style="margin-bottom:2%;" name="showAllEntries" class="socketchatbox-messageBody socketchatbox-messageBody-me" id="showAllEntries" type="button">Prikaži vse vpise</button>'

                    $(".socketchatbox-chatArea").append(reply_others);

                }
                else {
                    localStorage.setItem("disableAllEntries",0);
                }


                saveElement(reply_others);

                i+=1;
                
                disable_input(false);

                try {
                    document.getElementById("showAllEntries").scrollIntoView({behavior: "smooth"});
                }
                catch(err){
                    console.log("ERROR ",err)
                }

                $("#inputField").focus();
            }

            else if (response_type == "waitingTimes") {
                    //DATA IS LIST OF JSON OBJECTS
                    for (var k = 0; k < data.length; k++) {
                    var keys = Object.keys(data[k]);
                    var slo_keys = ["Bolnišnica","Telefon","E-mail","Sprejem"];

                    var oldDateFormat = new Date(data[k]['date']);
                    data[k]['date'] = oldDateFormat.toLocaleDateString();

                    var reply_others = '<div style="padding:0;" class="socketchatbox-message-wrapper" id="wrapper' + j + i + '"><div id="holder' + j + i + '" class="socketchatbox-message socketchatbox-message-others"><span style="margin-top:1%;margin-bottom:1%;width:300px;" id="data' + j + i + '" class="socketchatbox-messageBody socketchatbox-messageBody-others">'


                    for (var l = 0; l < keys.length; l++) {
                        if (typeof(data[k][keys[l]]) == 'object'){
                            reply_others += slo_keys[l] + ": ";
                            reception = data[k][keys[l]];

                            reception_keys = Object.keys(reception);

                            if (reception[reception_keys[1]] == 1){
                                reply_others += reception[reception_keys[0]] + "<br>" + "(čez " + reception[reception_keys[1]] + " dan)";
                            }
                            else {
                                reply_others += reception[reception_keys[0]] + "<br>" + "(čez " + reception[reception_keys[1]] + " dni)";
                            }

                        }
                        else {
                            reply_others += slo_keys[l] + ": " + data[k][keys[l]] + "<br>";
                        }
                    };

                    reply_others += '</span></div></div>';

                    $(".socketchatbox-chatArea").append(reply_others);

                    saveElement(reply_others);

                    i+=1;
                }
                disable_input(false);

                $("#inputField").focus();
            }

            else if (response_type == "userInfo") {
                //DATA IS USER INFO
                var keys = Object.keys(data);
                var slo_keys = ["Ime","Priimek","Spol","Datum rojstva"];

                if (data['gender'] == "MALE"){
                    data['gender'] = "Moški"
                }
                else {
                    data['gender'] = "Ženski";
                };


                var oldDateFormat = new Date(data['dateofbirth']);
                data['dateofbirth'] = oldDateFormat.toLocaleDateString();

                reply_others = '<div style="padding:0;" class="socketchatbox-message-wrapper" id="wrapper' + j + i + '"><div id="holder' + j + i + '" class="socketchatbox-message socketchatbox-message-others"><span style="margin-top:1%;margin-bottom:2%;width:300px;" id="data' + j + i + '" class="socketchatbox-messageBody socketchatbox-messageBody-others">'

                for (var l = 0; l < keys.length; l++) {
                    reply_others += slo_keys[l] + ": " + data[keys[l]] + "<br>"
                };

                reply_others += '</span></div></div>';

                $(".socketchatbox-chatArea").append(reply_others);

                saveElement(reply_others);

                i+=1;

                disable_input(false);

                $("#inputField").focus();

                document.getElementById("data" + j + (i-1)).scrollIntoView({behavior: "smooth"});

            }

            else if (response_type == "button") {
                //DATA GIVES OPTIONS FOR USER

                for (var k = 0; k < data.length; k++) {
                    var new_button = '<button name="getE ' + data[k]['value'] + '" class="choice_btn socketchatbox-messageBody socketchatbox-messageBody-me" id="btn' + i + j + '" type="button">' + data[k]['name'] + '</button>';
                    $(".socketchatbox-chatArea").append(new_button);

                    localStorage.setItem("button" + k,new_button);

                    i += 1;
                }

                localStorage.setItem("buttonIndex",data.length);

                document.getElementById("btn" + (i-1) + j).scrollIntoView({behavior: "smooth"});
            }

            else if (response_type == "search") {
                console.log(data);

                if (data.length >= 3){
                    maxEntries = 3
                }
                else {
                    maxEntries = data.length
                }


                for (var i = 0; i < maxEntries; i++) {
                    console.log(" @ SEARCH in chatboxjs")
                    // reply_others = '<div style="padding-bottom:1%;" class="socketchatbox-message-wrapper" id="wrapper-others' + j + '"><div class="socketchatbox-message socketchatbox-message-others"><div class="socketchatbox-username">DialogFlow<span class="socketchatbox-messagetime">' + date + '</span></div><span class="socketchatbox-messageBody socketchatbox-messageBody-others">' + data[i]["name"] + '<button name="getE ' + data[i]['index'] + '" class="choice_btn socketchatbox-messageBody socketchatbox-messageBody-me" id="btn' + i + j + '" type="button">' + data[i]['value'] + '</button></span><br></div></div>'
                    reply_others = '<div style="padding-bottom:1%;" class="socketchatbox-message-wrapper" id="wrapper-others' + j + '"><div class="socketchatbox-message socketchatbox-message-others"><span class="socketchatbox-messageBody socketchatbox-messageBody-others">' + data[i]["name"] + ': ' + data[i]['value'] + '</span><br></div></div>'

                    saveElement(reply_others);

                    reply_others = '<div style="padding-bottom:1%;" class="socketchatbox-message-wrapper choice_btn_wrapper" id="wrapper-others' + j + '"><div class="socketchatbox-message socketchatbox-message-others"><span class="socketchatbox-messageBody socketchatbox-messageBody-others">' + data[i]["name"] + ':<br><button style="margin-top:1%;" name="getE ' + data[i]['index'] + '" class="choice_btn socketchatbox-messageBody socketchatbox-messageBody-me" id="btn' + i + j + '" type="button">' + data[i]['value'] + '</button></span><br></div></div>'

                    $(".socketchatbox-chatArea").append(reply_others);

                    
                }

                indices = [];

                for (var i = 0; i < data.length; i++) {
                    indices.push(data[i].index)
                }

                indices = new Set(indices);
                indices = Array.from(indices);

                $(".socketchatbox-chatArea").append('<button name="getE ' + indices + '" style="margin-bottom:2%;" class="choice_btn socketchatbox-messageBody socketchatbox-messageBody-me" id="showAllSearchResults" type="button">Prikaži vse rezultate iskanja</button>')


                console.log(" @ SEARCH in chatboxjs finished")

                //i+=1;

                localStorage.setItem("disableAllEntries",1);
                
                disable_input(false);

                $("#inputField").focus();

                document.getElementById("showAllSearchResults").scrollIntoView({behavior: "smooth"});

            }

        else if (response_type == "PatientList") {
            console.log(data)

            listOfPatients = "";

            for (var i = 0; i < data.length; i++) {
                listOfPatients = listOfPatients + data[i] + "<br>"
            }

            reply_others = '<div style="padding-bottom:1%;" class="socketchatbox-message-wrapper" id="wrapper-others' + j + '"><div class="socketchatbox-message socketchatbox-message-others"><span class="socketchatbox-messageBody socketchatbox-messageBody-others" style="width:200px;">' + listOfPatients + '</span><br></div></div>';

            $(".socketchatbox-chatArea").append(reply_others);

            disable_input(false);

            $("#inputField").focus();

            document.getElementById("wrapper-others" + j).scrollIntoView({behavior: "smooth"});

        }

        else if (response_type == "getHelp") {
            console.log(data)

            listOfPatients = "";

            for (var i = 0; i < data.length; i++) {
                listOfPatients = listOfPatients + data[i] + "<br><br>"
            }

            reply_others = '<div style="padding-bottom:1%" class="socketchatbox-message-wrapper" id="wrapper-others' + j + '"><div class="socketchatbox-message socketchatbox-message-others"><span class="socketchatbox-messageBody socketchatbox-messageBody-others" style="width:300px;">' + listOfPatients + '</span><br></div></div>';

            $(".socketchatbox-chatArea").append(reply_others);

            disable_input(false);

            $("#inputField").focus();

            document.getElementById("wrapper-others" + j).scrollIntoView({behavior: "smooth"});

        }

           
        }
        catch(err) {
            console.log(err);
            //DIALOGFLOW RESPONSE DOES NOT CONTAIN DATA
            try {
                //return
            }
            catch(err){
            }

            if (response['url']) {
                try {
                    $("#URLiFrame").remove();
                }
                catch(err){}
                
                if (response_type != "search" || response_type != "entry") {
                    console.log("There was an error. This is the url: ", response['url']);
                    console.log(response_type);
                    //$("body").append('<iframe frameborder="0" style="overflow:hidden;height:100%;width:100%" id="URLiFrame" src="' + response['url'] + '" height="100%" width="100%"></iframe>')
                }
            }

            typing(0,"others");

            var reply_others = '<div class="socketchatbox-message-wrapper" id="wrapper-others' + j + '"><div class="socketchatbox-message socketchatbox-message-others"><div class="socketchatbox-username">DialogFlow<span class="socketchatbox-messagetime">' + date + '</span></div><span class="socketchatbox-messageBody socketchatbox-messageBody-others">' + response['text_answer'] +  '</span></div></div>';

            $(".socketchatbox-chatArea").append(reply_others);
            saveElement(reply_others);

            disable_input(false);

            $("#inputField").focus();

            document.getElementById("wrapper-others" + j).scrollIntoView({behavior: "smooth"});
        }

        date = cur_date();
    });
};

//SHOWS AND HIDES CHATBOX
$("#socketchatbox-top").click(function(element){
    if (element.target !== this || $("#login-page").is(":visible") || $("#logout-page").is(":visible")){
        return
    }

    console.log("It runs socketchatbox-top click");
    if ($("#socketchatbox-body").is(":visible")){
        $("#socketchatbox-showHideChatbox").text("↑");
    }
    else {
        $("#socketchatbox-showHideChatbox").text("↓");
        //LOAD SESSION STORAGE IF PAGE REFRESHED
        
    }

    $("#socketchatbox-body").toggle();

    setTimeout(function() {
        reload_session_storage();
    }, 100);

    $("#inputField").focus();
});

//OPENS LOGIN/LOGOUT PAGE
$("#toLogin").click(function(){
    if ($("#socketchatbox-showHideChatbox").html() != "↓"){
        console.log("This should now open the window")
        $("#socketchatbox-top").click(); 
        return
    }
    console.log("It runs login-logout click");

    try {
        if (sessionStorage.getItem("logged-in") != 1) {
            console.log("NOT LOGGED IN");
            height = $(".socketchatbox-page").height() -  $("#socketchatbox-top").height();
            width = $(".socketchatbox-page").width();
            console.log("BODY HEIGHT: " + height + " BODY WIDTH: " + width);
            $("#login-page").css({"height":height,"width":width});
            $("#socketchatbox-body").toggle();
            $("#login-page").toggle();
        }
        else {
            console.log("LOGGED IN");
            $("#logout-page").toggle();
            $("#socketchatbox-body").toggle();
        }
    }
    catch (err){
        console.log("NOT SET");
        $("#logout-page").toggle();
        $("#socketchatbox-body").toggle();
    }

});

//SENDS FORM TO DJANGO
$("#submit").click(function(e){
    e.preventDefault();
    console.log("    submitting ....");
    data = $("#login-form").serializeArray();
    var url = window.location.href + "login";

    $.post(url,data,function(response){
        response = JSON.parse(response);

        if (response["success"] == 1) {
            $("#login-page").hide();
            $("#logout-page").show();

            sessionStorage.setItem("logged-in", 1);
            sessionStorage.setItem("username", response["username"]);
            sessionStorage.setItem("patientInfo_name", response["name"]);
            sessionStorage.setItem("patientInfo_lastname", response["surname"]);
            sessionStorage.setItem("patientInfo_ehrid", response["ehrid"]);
            sessionStorage.setItem("patientInfo_isDoctor", response["isDoctor"]);
            sessionStorage.setItem("patientInfo_patients", response["patients"].toString());

            console.log(response["patients"].toString());

            $("#socketchatbox-username").text(response["username"]);
            $("#login-logout").css("background-color","green");

            global_username = response["username"];
            patientInfo_name = response["name"];
            patientInfo_lastname = response["surname"];
            patientInfo_ehrid = response["ehrid"];
            patientInfo_patients = JSON.parse(response["patients"]);
        }
        else {
            document.getElementById("info").innerHTML = response["message"]
            $("#info").show();
        }
        
    })
});

$("form").keydown(function(){
    $("#info").hide();
});

$("#logout").click(function(){
    var url = window.location.href + "logout";
    $.post(url,function(response){
        response = JSON.parse(response)
        console.log(response);
        $("#logout-page").hide();
        $("#login-page").show();
        sessionStorage.setItem("logged-in",0);
        sessionStorage.setItem("username",response["username"]);
        $("#socketchatbox-username").text(response["username"]);
        $("#login-logout").css("background-color","red");
        global_username = "Uporabnik";
        $(".socketchatbox-message-wrapper").remove();
        sessionStorage.setItem("index",0);
        $(".choice_btn").remove();
        $("#showAllEntries").remove();
        j = 0;
    })
});

//AUTOCOMPLETE WHEN USER IS DOCTOR
$(".socketchatbox-inputMessage-div").keyup(function(t){
    console.log(t.which, autocompleting);
    console.log($(this).children()[1].value);
    if (sessionStorage.getItem("patientInfo_isDoctor") == "true" && sessionStorage.getItem("logged-in") == 1 && (t.which >= 65 && t.which <= 90)  || (t.which >= 186 && t.which <= 222) || t.which == 8 || t.which == 16 || t.which == 32 || t.which == 8) {

        if (!autocompleting && t.which != 8) {
            if (t.which == 32) {
                autocompleting = 1
            }
            return
        }

        current_word = sessionStorage.getItem("current_word");

        var key = t.key.toLowerCase();
        console.log("FUCKING KEY IS: ",key);s
        var patients = JSON.parse(sessionStorage.getItem("patientInfo_patients"));


        if (current_word == null) {
            current_word = key;
            sessionStorage.setItem("current_word",current_word);
        }
        else if (t.which == 8) {
            if (autocompleting) {
                current_word = current_word.slice(0,-1);
                sessionStorage.setItem("current_word",current_word);
                console.log("Word after deleting: " + current_word);

                if (current_word.length <= 2) {
                    $("#autocomplete").html("");
                    $("#autocomplete").css("display","none");
                }
            }
            else {
                console.log("autocompleting is 0!!!");
                current_word = $(this).children()[1].value.split(" ");
                current_word = current_word[current_word.length - 1];
                sessionStorage.setItem("current_word",current_word);

                if (current_word.length <= 2) {
                    $("#autocomplete").html("");
                    $("#autocomplete").css("display","none");
                }
            }
        }
        else if (t.which == 16) {
            return
        }
        else {
            current_word = current_word + key;
            sessionStorage.setItem("current_word",current_word);
        }

        console.log("CURRENT WORD IS : "  + current_word);


        for (var i = 0; i < patients.length; i++) {
            console.log("Checking " + patients[i] + " with " + current_word);
            if (patients[i].startsWith(current_word) && current_word.length > 2) {
                console.log("Recommendation is: " + patients[i]);
                $("#autocomplete").html(patients[i]);
                $("#autocomplete").css("display","block");
                autocompleting = 1;
                return;
            }
            
        }

        if (current_word.length > 2) {
            console.log("WHAT THE FUCK");
            sessionStorage.setItem("current_word","");
            if (t.which != 32) {
                autocompleting = 0;
            }
            $("#autocomplete").html("");
            $("#autocomplete").css("display","none");
        }

    }
    else {
        console.log("He's not a doc, we won't AUTOCOMPLETE!!!");
        sessionStorage.setItem("current_word","");
        autocompleting = 1;
        $("#autocomplete").html("");
        $("#autocomplete").css("display","none");
        return
    }
});

//USER CLICKS THE AUTOCOMPLETE SUGGESTION
$("#autocomplete").click(function(){
    var name = $(this).text();

    $("#autocomplete").html("");
    $("#autocomplete").css("display","none");

    current_word = sessionStorage.getItem("current_word");

    var cur_input = $(".socketchatbox-inputMessage").val();
    var new_input = cur_input.slice(0,cur_input.length-current_word.length) + name;

    $(".socketchatbox-inputMessage").val(new_input);
    $("#inputField").focus();
});

//USER CLICKS RIGHT ARROW THE AUTOCOMPLETE SUGGESTION
$(".socketchatbox-inputMessage-div").keydown(function(t){
    if (t.which != 39 || !$("#autocomplete").is(":visible")) {
        return
    }

    var name = $("#autocomplete").text();

    $("#autocomplete").html("");
    $("#autocomplete").css("display","none");

    current_word = sessionStorage.getItem("current_word");

    var cur_input = $(".socketchatbox-inputMessage").val();
    var new_input = cur_input.slice(0,cur_input.length-current_word.length) + name;

    $(".socketchatbox-inputMessage").val(new_input);
    $("#inputField").focus();
});

//PROCESSES DATA FROM INPUT FIELD WHEN USER CLICKS ENTER
$(".socketchatbox-page").keydown(function(t){
    if (t.which == 13) {
        $("#autocomplete").html("");
        $("#autocomplete").css("display","none");

        var message = $(".socketchatbox-inputMessage").val();

        if (message == "") {
            return
        }
        if (!message.replace(/\s/g, '').length) {
            return
        }

        document.getElementById("inputField").value =  "";

        date = cur_date();

        communicate(message,j);

        $("#inputField").focus();

        j += 1;
    }
});

//PROCESSES DATA FROM INPUT FIELD WHEN USER CLICKS THE BUTTON
$("#socketchatbox-sendFileBtn").click(function(t){
    $("#autocomplete").html("");
    $("#autocomplete").css("display","none");
    
    var message = $(".socketchatbox-inputMessage").val();

    if (message == "") {
        return
    }
    if (!message.replace(/\s/g, '').length) {
            return
    }

    document.getElementById("inputField").value =  "";

    date = cur_date();

    communicate(message,j);

    $("#inputField").focus();

    j += 1;    
});

//REMOVES CHOICE BUTTONS
$(document).on("click", ".choice_btn", function(){
    message1 = document.getElementById(event.target.id).name;
    message2 = document.getElementById(event.target.id).innerHTML;
    message = [message1,message2];
    $(this).parent().parent().parent().removeClass("choice_btn_wrapper");
    $(".choice_btn_wrapper").remove();
    $(".choice_btn").fadeOut(100, function(){ $(this).remove();});
    console.log("++++ USER MESSAGE ++++  >  " + message);
    communicate(message,j);
    j += 1;
});

//READS CHOICE BUTTONS
$(document).on("click", "#showAllEntries", function(){
    $("#showAllEntries").fadeOut(100, function(){ $(this).remove();});
    buttonIndex = localStorage.getItem("buttonIndex");

    for (var i = 0; i < buttonIndex; i++) {
        var new_button = localStorage.getItem("button" + i);
        $(".socketchatbox-chatArea").append(new_button);
    }

    console.log("Last button id: " + localStorage.getItem("button" + (buttonIndex - 1)).id);

    //document.getElementById("btn" + (i-1) + j).scrollIntoView({behavior: "smooth"});
});


//BOX RESIZING
var a = -1
  , i = -1
  , s = null;

$(".socketchatbox-resize").mousedown(function(event) {
    a = event.clientX; 
    i = event.clientY; 
    s = $(this).attr("id"),
    event.preventDefault(),
    event.stopPropagation()
});

$(document).mousemove(function(event) {
    if ($("#login-page").is(":visible")) {
        return
    }

    if (-1 != a) {
        var t = $("#socketchatbox-body").outerWidth()
          , o = $("#socketchatbox-body").outerHeight()
          , c = event.clientX - a
          , r = event.clientY - i;
        s.indexOf("n") > -1 && (o -= r),
        s.indexOf("w") > -1 && (t -= c),
        s.indexOf("e") > -1 && (t += c),
        250 > t && (t = 250),
        70 > o && (o = 70),
        $("#socketchatbox-body").css({
            width: t + "px",
            height: o + "px"
        }),
        a = event.clientX,
        i = event.clientY
    }
});

$(document).mouseup(function() {
    a = -1,
    i = -1
});
