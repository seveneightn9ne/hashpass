function supports_html5_storage() {
    try {
        return 'localStorage' in window && window['localStorage'] !== null;
    } catch (e) {
        return false;
    }
}

var LOCAL_MASTER_HASH_KEY = "master_hash";
var LOCAL_MASTER_SALT_KEY = "master_salt";

function save_master(master) {
    var salt = forge.random.getBytesSync(128);
    var hashed_master = forge.md.sha512.create().update(master + salt).digest().toHex();
    localStorage.setItem(LOCAL_MASTER_HASH_KEY, hashed_master);
    localStorage.setItem(LOCAL_MASTER_SALT_KEY, salt);
}

function saved_master() {
    return {
        hash: localStorage.getItem(LOCAL_MASTER_HASH_KEY),
        salt: localStorage.getItem(LOCAL_MASTER_SALT_KEY)
    };
}

function has_saved_master() {
    var pass_struct = saved_master()
    return pass_struct.hash != null && pass_struct.salt != null;
}

function clear_saved_master() {
    localStorage.removeItem(LOCAL_MASTER_HASH_KEY);
    localStorage.removeItem(LOCAL_MASTER_SALT_KEY);
}

function check_master(entered_master) {
    var pass_struct = saved_master();
    var hashed_master = forge.md.sha512.create().update(entered_master + pass_struct.salt).digest().toHex();
    return hashed_master === pass_struct.hash;
}

$(document).ready(function() {
    // Security warning.
    if (location.protocol === 'https:' || location.protocol === "file:") {
        $(".insecure-warning").hide();
    } else {
        console.warn("Insecure connection, please use https.");
        $("#main-title").addClass("strike");
    }

    var hp = new HashPass();

    function recalculate_result() {
        var master_val = $("#master").val();
        var website_val = $("#website").val();
        if (master_val === "" || website_val === "") {
            $("#password").val("");
        } else {
            var pass = hp.make_password(master_val, website_val);
            $("#password").val(pass);
        }
    }

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
        recalculate_result();
    });

    function onsave() {
        save_master($("#master").val());
        $("#save").fadeOut();
        $("#clear").show();
        $("#master").addClass("correct");
    };

    $("#save").click(onsave);

    $("#clear").click(function() {
        clear_saved_master();
        $(this).fadeOut();
        $("#save").show();
        $("#master").val("");
        $("#master").removeClass("correct incorrect");
        recalculate_result();
        return false;
    });

    $("#website").on('input', function() {
        recalculate_result();
    });

    $("#master").keyup(function(e){
        if(e.keyCode == 13) {
            onsave();
            recalculate_result();
            $("#website").focus();
        }
    });

    $("#website").keyup(function(e){
        if(e.keyCode == 13) {
            recalculate_result();
            $("#password").attr("disabled",false);
            $("#password").select();
        }
    });

    $("#password").blur(function() {
        $(this).attr("disabled", true);
    });

});
