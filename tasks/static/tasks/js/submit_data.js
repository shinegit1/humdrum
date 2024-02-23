let upload_file =document.getElementById("UploadFileData");
let upload_text = document.getElementById("UploadTextData");

function showText(){
    upload_file.style.display ='none';
    upload_text.style.display ='block';
};

function showFile(){
    upload_file.style.display ='block';
    upload_text.style.display ='none';
};
