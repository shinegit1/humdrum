// change eye icon to show and hide in input password type
let show_eye = document.getElementById("ShowEye");
let hide_eye = document.getElementById("HideEye");

function check_show_hide(password, show_eye, hide_eye){
    if (password.type === "password") {
        password.type ="text";
        show_eye.style.display ='block';
        hide_eye.style.display ='none';
    } else {
        password.type ="password";
        show_eye.style.display ='none';
        hide_eye.style.display ='block';
    }
};

// show and hide password in the login and signup box
function password_show_hide() {
    let password = document.getElementById("id_password");
    check_show_hide(password, show_eye, hide_eye);
};

// show and hide confirm password in the login box
function password1_show_hide() {
    let password = document.getElementById("id_password1");
    check_show_hide(password, show_eye, hide_eye);
};

// show and hide confirm password in the signup box
function password2_show_hide() {
    let password = document.getElementById("id_password2");
    let show = document.getElementById("ShowEye2");
    let hide = document.getElementById("HideEye2");
    check_show_hide(password, show, hide);
};
