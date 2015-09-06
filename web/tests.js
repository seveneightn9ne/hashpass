"use strict";
var hashpasslib = require('./hashpasslib');

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
