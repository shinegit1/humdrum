// show all comments when button clicked
let comment_button =document.getElementById("ShowCommentButton");
let comment_box =document.getElementById("CommentBox");

function show_comments() {
    comment_box.style.display ='block';
    comment_button.style.display ='none';
};

function hide_comments() {
    comment_box.style.display ='none';
    comment_button.style.display ='block';
};

// direct go to textarea box when button clicked
function go_to_textarea(clicked){
    document.getElementById("id_comment").focus();
};

// add placeholder attribute in textarea
let textarea_add_placeholder =document.getElementById("id_comment");
textarea_add_placeholder.setAttribute("placeholder", "Type your comment here...");

function show_nested_comments(child_comment, plus, minus) {
    child_comment.style.display ="block";
    plus.style.display ="none";
    minus.style.display ="block";
};

function hide_nested_comments(child_comment, plus, minus){
    child_comment.style.display ="none";
    plus.style.display ="block";
    minus.style.display ="none";
}


// hide and show the nested comment list
function nested_comments(clicked) {
    let child_comment_id ="ChildComments-"+clicked;
    let plus_icon_id ="PlusIcon-"+clicked;
    let minus_icon_id ="MinusIcon-"+clicked;
    let child_comment =document.getElementById(child_comment_id);
    let plus =document.getElementById(plus_icon_id);
    let minus =document.getElementById(minus_icon_id);
    if (child_comment.style.display =="block") {
        hide_nested_comments(child_comment, plus, minus);
    } else {
        show_nested_comments(child_comment, plus, minus)
    }
};
