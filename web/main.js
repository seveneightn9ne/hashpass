require(["./hashpasslib", "./whiplash"], function(hashpasslib, whiplash) { // Start of module.

var LOCAL_MASTER_HASH_KEY = "master_hash";

function save_master(master, cb_progress, cb_finished) {
    var salt = TwinBcrypt.genSalt(13);
    var hashed_master = TwinBcrypt.hash(master, salt, cb_progress, function(hashed) {
        localStorage.setItem(LOCAL_MASTER_HASH_KEY, hashed);
        cb_finished();
    });
}

function saved_master() {
    return localStorage.getItem(LOCAL_MASTER_HASH_KEY);
}

function has_saved_master() {
    return saved_master() != null;
}

function clear_saved_master() {
    localStorage.removeItem(LOCAL_MASTER_HASH_KEY);
}

function check_master(entered_master, cb_progress, cb_finished) {
    return TwinBcrypt.compare(entered_master, saved_master(), cb_progress, cb_finished);
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

    var bcrypt_compute_marker = {};

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
            var passwd = make_site_password(master_val, website_val);
            $("#password").val(passwd);
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

        // Cause previous comparisons to stop.
        var local_bcrypt_compute_marker = {};
        bcrypt_compute_marker = local_bcrypt_compute_marker;

        update_save_ui();

        $(this).removeClass("correct incorrect thinking");
        if ($(this).val() == "") {
            return;
        }

        if (has_saved_master()) {
            $(this).addClass("thinking");
            check_master($(this).val(), function(p) {
                return bcrypt_compute_marker === local_bcrypt_compute_marker;
            }.bind(this), function(matched) {
                $(this).removeClass("correct incorrect thinking");
                if (matched) {
                    $(this).addClass("correct");
                } else {
                    if ($(this).val() != "") {
                        $(this).addClass("incorrect");
                    } else {
                        $(this).removeClass("incorrect");
                    }
                }
            }.bind(this));
        }

        recalculate_result();
    });

    function onsave() {
        clearing_timer.bump();
        var local_bcrypt_compute_marker = {};
        bcrypt_compute_marker = local_bcrypt_compute_marker;
        save_master($("#master").val(), function(p) {
            return bcrypt_compute_marker === local_bcrypt_compute_marker;
        }, function() {
            update_save_ui();
        });
        $("#save").fadeOut();
    };

    function update_save_ui() {
        if (has_saved_master()) {
            $("#save").fadeOut();
            $("#clear").show();
        } else {
            $("#save").show();
            $("#clear").hide();
        }
    }

    $("#save").click(onsave);

    $("#clear").click(function() {
        clearing_timer.bump();

        // Cancel existing computations.
        bcrypt_compute_marker = {};

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
