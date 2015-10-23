require(["./hashpasslib", "./whiplash"], function(hashpasslib, whiplash) { // Start of module.

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

function make_timer(ms, callback) {
    var id = null;

    return {
        bump: function() {
            clearTimeout(id);
            setTimeout(function() {
                id = null;
                callback();
            }, ms);
        }
    }
}

$(document).ready(function() {
    // Security warning.
    if (location.protocol === 'https:' || location.protocol === "file:") {
        $(".insecure-warning").hide();
    } else {
        console.warn("Insecure connection, please use https.");
        $("#main-title").addClass("strike");
    }

    var make_password_channel = whiplash.make_channel(hashpasslib.make_password);

    // Clear the password fields after 1 minute of inactivity.
    var clearing_timer = make_timer(60*1000, function() {
        console.log("Clearing password fields after timeout.");
        $("#master").val("");
        $("#website").val("");
        recalculate_result();
    });

    // The timer needs to be bumped on any reasonable interaction.
    clearing_timer.bump();

    function recalculate_result() {
        var master_val = $("#master").val();
        var website_val = $("#website").val();
        if (master_val === "" || website_val === "") {
            $("#password").val("");
        } else {
            $("#password").val("...");
            // Use the "make_password" channel.
            make_password_channel(master_val, website_val, function(pass) {
                $("#password").val(pass);
            });
        }
    }

    if (has_saved_master()) {
        $("#save").hide();
    } else {
        $("#clear").hide();
    }
    $("#master").focus();

    $("#master").on('input', function() {
        clearing_timer.bump();
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
        clearing_timer.bump();
        save_master($("#master").val());
        $("#save").fadeOut();
        $("#clear").show();
        $("#master").addClass("correct");
    };

    $("#save").click(onsave);

    $("#clear").click(function() {
        clearing_timer.bump();
        clear_saved_master();
        $(this).fadeOut();
        $("#save").show();
        $("#master").val("");
        $("#master").removeClass("correct incorrect");
        recalculate_result();
        return false;
    });

    $("#website").on('input', function() {
        clearing_timer.bump();
        recalculate_result();
    });

    $("#master").keyup(function(e){
        if(e.keyCode == 13) {
            clearing_timer.bump();
            onsave();
            recalculate_result();
            $("#website").focus();
        }
    });

    $("#website").keyup(function(e){
        if(e.keyCode == 13) {
            clearing_timer.bump();
            recalculate_result();
            $("#password").select();
        }
    });

    $("#password").focus(function() {
    	$(this).select();
    });

});

}); // End of module.
