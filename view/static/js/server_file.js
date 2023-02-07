function reloadFileList_pic(){
    $("#sFileList_pic").html('');
    $.ajax({
        url: "/server/sFileList_pic",
        type: "POST",
        async: false,
        dataType: "json",
        contentType: "application/json",
        success: function(res){
            for(let fileListLine of res.ret){
                let code = `<div class="sFileList_pic">${fileListLine}</div>`;
                $("#sFileList_pic").append(code);
            }
        }
    });
}
function reloadFileList_vid(){
    $("#sFileList_vid").html('');
    $.ajax({
        url: "/server/sFileList_video",
        type: "POST",
        async: false,
        dataType: "json",
        contentType: "application/json",
        success: function(res){
            for(let fileListLine of res.ret){
                let code = `<div class="sFileList_vid">${fileListLine}</div>`;
                $("#sFileList_vid").append(code);
            }
        }
    });
}
function deleteFile(){
    $("#deleteBtn").on("click", function(){
        $.ajax({
            url: "/file/aDeleteFiles",
            type: "POST",
            async: true,
            dataType: "json",
            contentType: "application/json",
            data: JSON.stringify({fileName : $("#deleteInp").val()}),
            success: function(res){
                reloadFileList();
            }
        });
    });
}

$(document).ready(function(){
    history.pushState(null, null, location.href);
    window.onpopstate = function () {
        history.go(1);
    };
    reloadFileList_pic();
    reloadFileList_vid();
    deleteFile();
    uploadFile();
});