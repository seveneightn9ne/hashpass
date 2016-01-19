define(function() { // Start of module.

// Salt for generating intermediate. (10 rounds)
// REUSED_BCRYPT_SALT = bcrypt.gensalt(rounds=10)
// The work factor is so low because phones have to run this too.
// Uses the 2y prefix compatible with both our js and py libs.
REUSED_BCRYPT_SALT = "$2y$10$w1dpoPu1duVEV4rnZPAkLe"
// Rounds to use for storage.
STORE_BCRYPT_ROUNDS = 13

var LETTERS = "abcdefghjkmnopqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXY";
var NUMBERS = "3456789";
var SYMBOLS = "#*@()+={}?";

var make_intermediate = function(secret_master, cb_progress, cb_success) {
  _check_bcrypt_input(secret_master);
  TwinBcrypt.hash(secret_master, REUSED_BCRYPT_SALT, cb_progress, cb_success)
};

var make_site_password = function(secret_intermediate, slug) {
  // Generate a site password from the secret_intermediate and site name.
  // 1. Concatenate (slug, generation, counter) separated by newlines.
  // 2. Hash (HMAC-Sha256) with secret_intermediate as the key.
  // 3. Truncate and convert to output character set.
  // 4. Try again with counter++ if candidate does not satisfy constraints.
  // Args:
  //     secret_intermediate: The secret component derived from the master.
  //     slug: The site name.
  // Returns:
  //     The password for the site, which is:
  //     - 20 characters
  //     - is_good_pass
  //     - deterministic
  var limit = 10000;
  var generation = 0;
  for (var counter = 0; counter < limit; counter++) {
    var combined = slug + "\n" + generation + "\n" + counter;
    var hashed_string = _hash(secret_intermediate, combined);
    var candidate = hashed_string.substring(0, 20);
    if (is_good_pass(candidate)) {
      return candidate;
    }
  }

  console.error("Could not find password after "+limit+" tries.");
  console.error("This is improbable or something is wrong.");
  throw new Error("Password reroll limit reached");
};

var is_good_pass = function(password) {
  // If the password contains a letter, numberd, and symbol, it is good.
  function contains_some(sample, approved) {
      // Whether sample string contains any characters from approved string.
      var approved_array = approved.split("")
      var count = approved_array.filter(function(c) {
          return sample.indexOf(c) != -1
      }).length
      return count > 0
  }
  return (contains_some(password, LETTERS) &&
          contains_some(password, NUMBERS) &&
          contains_some(password, SYMBOLS))
};

var make_storeable = function(secret_master, cb_progress, cb_success) {
  _check_bcrypt_input(secret_master);
  TwinBcrypt.hash(secret_master, TwinBcrypt.genSalt(STORE_BCRYPT_ROUNDS), cb_progress, cb_success)
}

var check_stored = function(secret_master, stored_component, cb_progress, cb_success) {
  _check_bcrypt_input(secret_master);
  try {
    TwinBcrypt.compare(secret_master, stored_component, cb_progress, cb_success);
  } catch (e) {
    cb_success(false);
  };
}

var _chunks = function(lst, size) {
  if (size === undefined) {
      size = 3
  }
  var r = []
  for (var i = 0; i < lst.length / size; i++) {
      r.push(lst.slice(size*i, size*(i+1)))
  }
  return r
};

var _bytes_to_pw_chars = function(nums) {
  // Three 8-bit numbers map to a string of 4 password-safe characters.
  var charset = LETTERS + NUMBERS + SYMBOLS;
  if (charset.length != 64) {
      throw new Error("Bad charset wrong length");
  }
  var nums4 = [( nums[0] & 0xFC) >> 2,
      ((nums[0] & 0x3)  << 4) | ((nums[1] & 0xF0) >> 4),
      ((nums[1] & 0x0F) << 2) | ((nums[2] & 0xC0) >> 6),
      nums[2] & 0x3F];

  return nums4.map(function (num) {
      return charset[num]
  }).reduce(function (a, b) {
      return a + b
  });
};

var _hash = function(secret, data) {
  // HMAC-SHA256 hash the string and convert to the 64 character charset.
  function ord(chr) {
      return chr[0].charCodeAt(0);
  }
  var hmac = forge.hmac.create();
  hmac.start("sha256", secret);
  hmac.update(data);
  var hashed = hmac.digest();
  var nums = hashed.data.split("").map(ord)
  return _chunks(nums).map(_bytes_to_pw_chars).reduce(function (a, b) {
      return a + b
  });
};


function _check_bcrypt_input(x) {
  if (x.length > 72) {
    console.error("Bcrypt does not support passwords longer than 72 bytes.");
    throw new Error("Bcrypt limit exceeded.");
  }
}

// Export from module.
return {
  make_intermediate: make_intermediate,
  make_site_password: make_site_password,
  is_good_pass: is_good_pass,
  make_storeable: make_storeable,
  check_stored: check_stored,
  _bytes_to_pw_chars: _bytes_to_pw_chars,
  _hash: _hash
}

}); // End of module.
