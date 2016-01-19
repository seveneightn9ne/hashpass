require(["./hashpasslib"], function(hashpasslib) { // Start of module.

mocha.setup('tdd');
mocha.checkLeaks();
mocha.run();

suite("HashPassAlg", function() {
  setup(function() {
    this.intermediates = [
      "$2y$10$w1dpoPu1duVEV4rnZPAkLe8kxqbSe4xmE4jVqL4IcwVLWluqZNI3G",
      "$2y$10$w1dpoPu1duVEV4rnZPAkLea0PzJXKXtAHtHZ60MWk6pk1GH1uKpSe"
    ];

    this._test_site = function(rerolls, intermediate, slug, expected) {
      // Test one site password, ignores the reroll parameter.
      expect(hashpasslib.make_site_password(intermediate, slug)).to.equal(expected);
    };
  });

  test("make_intermediate too long", function() {
    var x73 = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx";
    expect(function() {
      hashpasslib.make_intermediate(x73, function(){}, function() {})
    }).to.throwException(new Error("Bcrypt limit exceeded."));
  });

  var SLOW_LIMIT = 20000;

  test("make_intermediate", function(done) {
    this.timeout(SLOW_LIMIT);
    hashpasslib.make_intermediate("1234", function(){}, function(result) {
      expect(result).to.equal("$2y$10$w1dpoPu1duVEV4rnZPAkLe8kxqbSe4xmE4jVqL4IcwVLWluqZNI3G");
      done();
    });
  });
  test("make_intermediate", function(done) {
    this.timeout(SLOW_LIMIT);
    hashpasslib.make_intermediate("super secret", function(){}, function(result) {
      expect(result).to.equal("$2y$10$w1dpoPu1duVEV4rnZPAkLea0PzJXKXtAHtHZ60MWk6pk1GH1uKpSe");
      done();
    });
  });
  test("make_intermediate", function(done) {
    this.timeout(SLOW_LIMIT);
    hashpasslib.make_intermediate("blowfish", function(){}, function(result) {
      expect(result).to.equal("$2y$10$w1dpoPu1duVEV4rnZPAkLefQ9jBvhg/MM6m/oTFbWLBq0R0bhwiVW");
      done();
    });
  });

  test("is_good_pass", function() {
    expect(hashpasslib.is_good_pass("a4#aaaaaaaaaaaaaaaaa")).to.be(true);
    expect(hashpasslib.is_good_pass("oooo6o#ooaaaaaaaaaaa")).to.be(true);
    expect(hashpasslib.is_good_pass("")).to.be(false);
    expect(hashpasslib.is_good_pass("oeuoeuOOO2343")).to.be(false);
  });

  test("make_storeable", function(done) {
    this.timeout(SLOW_LIMIT);
    var secret = "abcdef";
    hashpasslib.make_storeable(secret, function(){}, function(storeable) {
      TwinBcrypt.compare(secret, storeable, function(){}, function(result) {
        expect(result).to.be(true);
        done();
      });
    });
  });

  test("check_stored accept", function(done) {
    // Test with an 11 round bcrypt.
    var secret = "blowfish";
    var stored = "$2y$11$Gzhmkebfiz2OapRqu/zWSOH2Wa9uAsbb4Vd5q3iKBILsMRX8MBpQa";
    hashpasslib.check_stored(secret, stored, function(){}, function(result) {
      expect(result).to.be(true);
      done();
    });
  });

  test("check_stored reject", function(done) {
    // Test with an 11 round bcrypt.
    var secret = "blowfish";
    // This stored hash does not match the secret.
    var stored = "$2y$11$Gzhmkebfiz2OapRqu/zwSOH2Wa9uAsbb4Vd5q3iKBILsMRX8MBpQa";
    hashpasslib.check_stored(secret, stored, function(){}, function(result) {
      expect(result).to.be(false);
      done();
    });
  });

  test("check_stored reject fail", function(done) {
    // Test with an 11 round bcrypt.
    var secret = "blowfish";
    // This stored hash does not match the secret.
    var stored = "bogus";
    hashpasslib.check_stored(secret, stored, function(){}, function(result) {
      expect(result).to.be(false);
      done();
    });
  });

  test("bytes_to_pw_chars", function() {
    expect(hashpasslib._bytes_to_pw_chars([0, 0, 0])).to.equal("aaaa");
    expect(hashpasslib._bytes_to_pw_chars([255, 255, 255])).to.equal("????");
    expect(hashpasslib._bytes_to_pw_chars([4,32,196])).to.equal("bcde");
  });

  test("hmac", function() {
    var hmac = forge.hmac.create();
    hmac.start("sha256", "Jefe");
    hmac.update("what do ya want for nothing?");
    var out = hmac.digest();
    expect(out.toHex()).to.equal("5bdcc146bf60754e6a042426089575c75a003f089d2739839dec58b964ec3843");
    expect(out.data[0]).to.equal("\x5b");
    expect(out.data[0].charCodeAt(0)).to.equal(91);
  });

  test("make_site_password with 0 and 1 rerolls", function() {
    // 0 rerolls.
    this._test_site(0, this.intermediates[0], "rhythm0", "V=tT8TuMj4YRa3=6}K(J")
    this._test_site(0, this.intermediates[1], "rhythm0", "@v*Y@?))NAHA+H)8@K(B")

    // 1 reroll.
    this._test_site(1, this.intermediates[0], "rhythm1", "Y)@5Q{KSVtLs{zyYpC8U")
    this._test_site(1, this.intermediates[1], "rhythm5", "6ufX@obn4KAoeJWWn*(z")
  });

  test("make_site_password with more rerolls", function() {
    // Higher reroll counts.
    this._test_site(2, this.intermediates[0], "rhythm151", "qcNq}+?KtdXL8*bawUda")
    this._test_site(3, this.intermediates[0], "rhythm354", "sRnjUBA36zV#MDAA=gMc")
    this._test_site(4, this.intermediates[0], "rhythm2435", "mdp5@sUT}9bBhjgE6RE7")
    this._test_site(5, this.intermediates[0], "rhythm30362", "?wn7SQytbo@v*+Q*sm#3")
    this._test_site(6, this.intermediates[0], "rhythm353402", "k@4J*sQ}YpY)bFNw53Fz")
  });
});

mocha.run();

}); // End of module.
