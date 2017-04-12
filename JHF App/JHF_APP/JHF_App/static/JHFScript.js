function convertFormToJSON(form){
    var array = $(form).serializeArray();
    var json = {};
    $.each(array, function(){
        json[this.name] = this.value || '';
    });
    json = JSON.stringify(json);
    return json;
}

$(document).ready(function(){
    $('form#adduser').bind('submit',function(event){
        event.preventDefault();
         alert("Help, is it running?");
        var form = this;
        var json = convertFormToJSON(form);
        $.ajax({
            type: "POST",
            url:  "/jhf/api/v1.0/users",
            data: json,
            contentType: "application/json; charset=utf-8",
            dataType : "json",
            success : function() {
                $("p").text(json);
            }
            error: function(err) {
                alert(err);
            }
        });
    });
});