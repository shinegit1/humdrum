// disappear or remove the success message Notification
let success_messages = document.getElementById("MessageNotification");

if (success_messages) {
    setTimeout(function() {
        success_messages.style.display = "none";
    }, 8000);
};

let error_message =document.getElementById("ErrorNotification");
if (error_message) {
    setTimeout(function() {
        error_message.style.display = "none";
    }, 8000);
};