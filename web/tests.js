"use strict";
var forge = require('node-forge');

var LETTERS = "abcdefghjkmnopqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXY"
var NUMBERS = "3456789"
var SYMBOLS = "#*@()+={}?"

function _to_chars(nums) {
    // Three 8-bit numbers map to a string of 4 password-safe characters.
    var charset = LETTERS + NUMBERS + SYMBOLS;
    if (charset.length !== 64) {
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
    })
}

function is_good_pass(password) {
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
}

function make_password_inner(master_plain, website) {
    var passwords = hashpasslib._chunks(
        hashpasslib.hash(website + master_plain), 20)
    while (true) {
        passwords = passwords.filter(
            hashpasslib.is_good_pass)
        if (passwords.length > 0) {
            return passwords[0]
        } else {
            passwords = hashpasslib._chunks(
                hashpasslib.hash("".join(passwords)), 20)
        }
    }
}

function _chunks(lst, size) {
    if (size === undefined) {
        size = 3
    }
    var r = []
    for (var i = 0; i < lst.length / size; i++) {
        r.push(lst.slice(size*i, size*(i+1)))
    }
    return r
}

function hash(string) {
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
}

var hashpasslib = {}
hashpasslib._to_chars = _to_chars
hashpasslib.is_good_pass = is_good_pass
hashpasslib.make_password_inner = make_password_inner
hashpasslib._chunks = _chunks
hashpasslib.hash = hash

exports.test_to_chars = function(test) {
    test.strictEqual(hashpasslib._to_chars([0, 0, 0]), "aaaa")
    test.strictEqual(hashpasslib._to_chars([255, 255, 255]), "????")
    test.strictEqual(hashpasslib._to_chars([4,32,196]), "bcde")
    test.done()
}

exports.test_is_good_pass = function(test) {
    test.strictEqual(hashpasslib.is_good_pass("a4#"), true)
    test.strictEqual(hashpasslib.is_good_pass("oooo6o#oo"), true)
    test.strictEqual(hashpasslib.is_good_pass(""), false)
    test.strictEqual(hashpasslib.is_good_pass("oeuoeuOOO2343"), false)
    test.done()
}

exports.test_make_password_inner = function(test) {
    test.strictEqual(
        hashpasslib.make_password_inner("a", "b"),
        "P4{tRc6X3q}5)bCw}su=")
    test.strictEqual(
        hashpasslib.make_password_inner("a", "sportsball"),
        "C}Kzk*)6(CbR}sM5PxuK")
    test.strictEqual(
        hashpasslib.make_password_inner("batterystapler", "sportsball"),
        "4D*y7}fP646v3rdWEMz6")
    test.done()
}
