function supports_html5_storage() {
    try {
        return 'localStorage' in window && window['localStorage'] !== null;
    } catch (e) {
        return false;
    }
}

var LOCAL_MASTER_KEY = "hashed_master";

function save_master(master) {
    var hashed_master = forge.md.sha512.create().update(master).digest().toHex();
    localStorage.setItem(LOCAL_MASTER_KEY, hashed_master);
}

function saved_master() {
    return localStorage.getItem(LOCAL_MASTER_KEY);
}

function has_saved_master() {
    return saved_master() != null;
}

function clear_saved_master() {
    localStorage.removeItem(LOCAL_MASTER_KEY);
}

function check_master(entered_master) {
    var hashed_master = forge.md.sha512.create().update(entered_master).digest().toHex();
    return hashed_master === saved_master();
}

$(document).ready(function() {
    // Security warning.
    if (location.protocol === 'https:') {
        $(".insecure-warning").hide();
    } else {
        console.warn("Insecure connection, please use https.");
        $("#main-title").addClass("strike");
    }

    var hp = new HashPass();
    if (has_saved_master()) {
        $("#save").hide();
    } else {
        $("#clear").hide();
    }
    $("#master").focus();

    $("#master").on('input', function() {
        if (has_saved_master()) {
            if (check_master($(this).val())) {
                $(this).addClass("correct");
                $(this).removeClass("incorrect");
            } else {
                $(this).removeClass("correct");
                if ($(this).val() != "") {
                    $(this).addClass("incorrect");
                } else {
                    $(this).removeClass("incorrect");
                }
            }
        }
    });

    function onsave() {
        save_master($("#master").val());
        $("#save").fadeOut();
        $("#clear").show();
        $("#master").addClass("correct");
    }

    $("#save").click(function() {
        onsave();
    });

    $("#website").on('input', function() {
        var pass = hp.make_password($("#master").val(), $(this).val());
        $("#password").val(pass);
    });

    $("#clear").click(function() {
        clear_saved_master();
        $(this).fadeOut();
        $("#save").show();
        $("#master").val("");
        return false;
    });

    $("#master").keyup(function(e){
        if(e.keyCode == 13) {
            onsave();
            $("#website").focus();
        }
    });

    $("#website").keyup(function(e){
        if(e.keyCode == 13) {
            $("#password").attr("disabled",false);
            $("#password").select();
        }
    });

    $("#password").blur(function() {
        $(this).attr("disabled", true);
    });

});
