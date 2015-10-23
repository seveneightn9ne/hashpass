// Solve the long response whiplash problem.
// If you have a long running request then
// old responses can come back after newer responses.
// Ideally, we want a request to cancel all old requests.

// Example usage:
// slowadd_channel = make_chanell(slowadd);
// onClick(function() {
//   slowadd_channel(a, b, function(r) {
//     view.display(r);
//   });
// };

define(function() { // Start of module.

function make_channel(fn) {
  var active_cb = null;

  return function channel_instance() {
    var noncb_args = Array.prototype.slice.call(arguments);
    var caller_cb = noncb_args.pop();

    function wrapped_cb(err, res) {
      // Only callback if this is the most recent cb.
      if (wrapped_cb === active_cb) {
        caller_cb(err, res);
      }
    }

    // Set the active cb to this one.
    active_cb = wrapped_cb;

    fn.apply(null, noncb_args.concat([wrapped_cb]));
  }
}

// Export from module.
return {
  make_channel: make_channel
}


}); // End of module.
