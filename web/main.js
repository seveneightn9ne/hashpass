require(["./hashpasslib", "./whiplash"], function(hashpasslib, whiplash) { // Start of module.

var LOCAL_MASTER_HASH_KEY = "master_hash";

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

function progress_circle_wrapper($element) {
    var progress_value = 0;

    var progress_circle = new ProgressCircle({
        canvas: $element.get(0),
        minRadius: 0.001,
        arcWidth: 12
    });

    progress_circle.addEntry({
        fillColor: "#777",
        fillColorComplete: "#fff",
        progressListener: function() {
            return progress_value;
        }
    });

    // $element.hide();

    return {
        update: function(p) {
            progress_value = p;
            progress_circle.update(p);
            if (p == 0) {
                // $element.hide();
            } else {
                // $element.show();
            }
        }
    };
}

// All the application state lives in this object.
// The outside world interacts by sending actions via the dispatch method.
// Each event will cause the render function (passed to init) to be called.
// This is inspired by flux.
var AppState = {
    init: function(renderfn) {
        this.external_render = renderfn;

        // Clear entered data after 5 minutes of inactivity.
        this.clearing_timer = make_timer(5*60*1000, function() {
            this.dispatch({type: "inactivity"});
        }.bind(this));

        this.master_content = "";
        this.master_state = "idle";
        this.slug_content = "";
        this.output_content = "";
        // Focus is special. It is cleared after setting by the consumer of the store.
        this.focus = "master";
        this.intermediate_progress = 0;

        // A handle is an object which is assosciated with a particular
        // (in this case active) execution of a task.
        // It is null when no task is occurring.
        this.save_handle = null;
        this.check_handle = null;
        this.intermediate_handle = null;

        this.intermediate = null;

        this.render();
    },
    ack_focus: function() {
        this.focus = null;
    },
    start_save: function() {
        var local_save_handle = this.save_handle = {};

        hashpasslib.make_storeable(this.master_content, function(p) {
            // Progress function.
            return local_save_handle === this.save_handle;
        }.bind(this),function(storeable) {
            // Finish function.
            if (local_save_handle !== this.save_handle) return;
            this.save_handle = null;

            localStorage.setItem(LOCAL_MASTER_HASH_KEY, storeable);
            this.dispatch({type: "master_save_finished"});
        }.bind(this));
    },
    stop_save: function() {
        this.save_handle = null;
    },
    start_check: function() {
        var local_check_handle = this.check_handle = {};
        var stored_component = localStorage.getItem(LOCAL_MASTER_HASH_KEY);
        this.master_state = "idle";
        if (stored_component == null || this.master_content.length == 0) {
            return;
        }

        // Wait a bit before starting the check.
        setTimeout(function() {
            if (local_check_handle !== this.check_handle) return;

            this.master_state = "thinking";
            this.dispatch({type: "master_check_started"});
            hashpasslib.check_stored(this.master_content, stored_component, function(p) {
                // Progress function.
                if (local_check_handle !== this.check_handle) return false;
                return true;
            }.bind(this),function(result) {
                // Finish function.
                if (local_check_handle !== this.check_handle) return;
                this.check_handle = null;

                if (result) {
                    this.master_state = "correct";
                } else {
                    this.master_state = "incorrect";
                }
                this.dispatch({type: "master_check_finished"});
            }.bind(this));
        }.bind(this), 350);
    },
    stop_check: function() {
        this.check_handle = null;
    },
    start_intermediate: function() {
        var local_intermediate_handle = this.intermediate_handle = {};
        this.intermediate = null;
        this.intermediate_progress = 0;
        if (this.master_content.length == 0) {
            return;
        }

        // Wait a bit before starting the intermediate.
        setTimeout(function() {
            if (local_intermediate_handle !== this.intermediate_handle) return;

            this.dispatch({type: "master_intermediate_started"});
            hashpasslib.make_intermediate(this.master_content, function(p) {
                // Progress function.
                if (local_intermediate_handle !== this.intermediate_handle) return false;
                this.intermediate_progress = p;
                this.dispatch({type: "progress_update"});
                return true;
            }.bind(this),function(intermediate) {
                // Finish function.
                if (local_intermediate_handle !== this.intermediate_handle) return;
                this.intermediate_handle = null;


                this.intermediate = intermediate;
                this.dispatch({type: "master_intermediate_finished"});
            }.bind(this));
        }.bind(this), 200);
    },
    stop_intermediate: function() {
        this.intermediate_handle = null;
    },
    update_output: function() {
        if (this.intermediate == null || this.slug_content.length == 0) {
            this.output_content = "";
            return;
        }
        var passwd = hashpasslib.make_site_password(this.intermediate, this.slug_content);
        this.output_content = passwd;
    },
    dispatch: function(action) {
        if (action.type != "progress_update") {
            console.log(action);
        }

        switch (action.type) {
        case "master_change":
            this.clearing_timer.bump();
            this.master_content = action.text;
            this.stop_save();
            this.start_check();
            this.start_intermediate();
            this.update_output();
            break;
        case "master_save":
            this.clearing_timer.bump();
            this.start_save();
            this.stop_check();
            this.master_state = "correct";
            break;
        case "master_save_finished":
            break;
        case "progress_update":
            break;
        case "master_check_started":
            break;
        case "master_check_finished":
            break;
        case "master_intermediate_started":
            break;
        case "master_intermediate_finished":
            this.update_output();
            break;
        case "master_clear":
            this.clearing_timer.bump();
            this.stop_save();
            this.stop_check();
            localStorage.removeItem(LOCAL_MASTER_HASH_KEY);
            this.master_state = "idle";
            break;
        case "master_return":
            this.focus = "slug";
            break;
        case "slug_change":
            this.clearing_timer.bump();
            this.slug_content = action.text;
            this.update_output();
            break;
        case "slug_return":
            this.focus = "output";
            break;
        case "output_touched":
            break;
        case "inactivity":
            console.log("Clearing password fields after timeout.");
            this.stop_save();
            this.stop_check();
            this.stop_intermediate();
            this.master_state = "idle";
            this.master_content = "";
            this.slug_content = "";
            this.output_content = "";
            this.intermediate_progress = 0;
            break;
        }

        this.render();
    },
    render: function() {
        var state = {
            master_content: this.master_content,
            master_state: this.master_state,
            slug_content: this.slug_content,
            output_content: this.output_content,
            focus: this.focus,
            saved_master: localStorage.getItem(LOCAL_MASTER_HASH_KEY),
            is_master_saving: this.save_handle != null,
            intermediate_progress: this.intermediate_progress
        }
        this.external_render(state);
    }
}

function ensure_jquery_val($element, val) {
    if ($element.val() != val) {
        $element.val(val);
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

    $("#save").hide();
    $("#clear").hide();
    $("#master").focus();

    var intermediate_progress_circle = progress_circle_wrapper($("#intermediate_progress_canvas"));

    AppState.init(function(state) {
        // Fill text fields.
        ensure_jquery_val($("#master"), state.master_content);
        ensure_jquery_val($("#website"), state.slug_content);
        ensure_jquery_val($("#password"), state.output_content);

        // Focus and select a textbok.
        if (state.focus == "master") {
            $("#master").focus();
        } else if (state.focus == "slug") {
            $("#website").focus();
        } else if (state.focus == "output") {
            $("#password").select();
        }
        AppState.ack_focus();

        // Set master coloring.
        $("#master").removeClass("correct incorrect thinking");
        $("#master").addClass(state.master_state);

        // Display save button.
        if (state.master_content.length > 0 && state.saved_master == null && !state.is_master_saving) {
            $("#save").fadeIn();
        } else {
            $("#save").fadeOut();
        }

        // Display clear button.
        if (state.saved_master != null || state.is_master_saving) {
            $("#clear").fadeIn();
        } else {
            $("#clear").fadeOut();
        }

        // Show intermediate progress only if a slug has been entered.
        if (state.slug_content.length > 0 && state.intermediate_progress > 0) {
            intermediate_progress_circle.update(state.intermediate_progress);
        } else {
            intermediate_progress_circle.update(0);
        }
    });

    $("#master").on('input', function() {
        AppState.dispatch({
            type: "master_change",
            text: $("#master").val()
        })
    });

    $("#master").keyup(function(e) {
        if(e.keyCode == 13) {
            AppState.dispatch({type: "master_return"});
        }
    });

    $("#website").on('input', function() {
        AppState.dispatch({
            type: "slug_change",
            text: $("#website").val()
        })
    });

    $("#website").keyup(function(e) {
        if(e.keyCode == 13) {
            AppState.dispatch({type: "slug_return"});
        }
    });

    $("#password").on('input', function() {
        AppState.dispatch({type: "output_touched"});
    });

    $("#password").keyup(function(e) {
        if(e.keyCode == 13) {
            AppState.dispatch({type: "output_touched"});
        }
    });

    $("#save").click(function() {
        AppState.dispatch({type: "master_save"});
    });

    $("#clear").click(function() {
        AppState.dispatch({type: "master_clear"});
    });
});

}); // End of module.
