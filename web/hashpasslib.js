
function HashPass() {
  var LETTERS = "abcdefghjkmnopqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXY";
  var NUMBERS = "3456789";
  var SYMBOLS = "#*@()+={}?";

  var _to_chars = function(nums) {
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

  var hash = function(string) {
    // SHA256 hash the string and convert to the 64 character charset.
    function ord(chr) {
        return chr[0].charCodeAt(0);
    }
    var hashed = forge.md.sha256.create()
        .update(string)
        .digest();
    var nums = hashed.data.split("").map(ord)
    return _chunks(nums).map(_to_chars).reduce(function (a, b) {
        return a + b
    });
  };

  this.make_password = function(master_plain, website) {
    var passwords = _chunks(
        hash(website + master_plain), 20)
    while (true) {
        passwords = passwords.filter(
            is_good_pass)
        if (passwords.length > 0) {
            return passwords[0]
        } else {
            passwords = _chunks(
                hash("".join(passwords)), 20)
        }
    }
  };
}
