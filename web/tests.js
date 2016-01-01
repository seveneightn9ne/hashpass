require(["./hashpasslib"], function(hashpasslib) { // Start of module.

mocha.setup('tdd');
mocha.checkLeaks();
mocha.run();

suite("HashPassAlg", function() {
  setup(function() {
    this.intermediates = [
      "$2y$13$X5A4.IjQghzyTGwc0wgRrebu3hlW/WFyN5GnvrTKvYsJtdsr5DXC6",
      "$2y$13$X5A4.IjQghzyTGwc0wgRrejiTwszgBLaN3PTew0gRtIrzb5EHsZB2"];

    this._test_site = function(rerolls, intermediate, slug, expected) {
      // Test one site password, ignores the reroll parameter.
      expect(hashpasslib.make_site_password(intermediate, slug)).to.equal(expected);
    };
  });

  test("make_intermediate too long", function() {
    var x73 = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx";
    expect(function() {
      hashpasslib.make_intermediate(x73, function() {})
    }).to.throwException(new Error("Bcrypt limit exceeded."));
  });

  test("make_intermediate", function(done) {
    this.timeout(5000);
    hashpasslib.make_intermediate("1234", function(result) {
      expect(result).to.equal("$2y$13$X5A4.IjQghzyTGwc0wgRrecUMeNiIgapq6zxM07dr3UDDdHUYWLTC");
      done();
    });
  });
  test("make_intermediate", function(done) {
    this.timeout(5000);
    hashpasslib.make_intermediate("super secret", function(result) {
      expect(result).to.equal("$2y$13$X5A4.IjQghzyTGwc0wgRrejDmecj5/NNmPPb5ok4tXNuhs/rdP5zy");
      done();
    });
  });
  test("make_intermediate", function(done) {
    this.timeout(5000);
    hashpasslib.make_intermediate("blowfish", function(result) {
      expect(result).to.equal("$2y$13$X5A4.IjQghzyTGwc0wgRrezL8JE8j/mpXN/V6YXoldoca002NMb0a");
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
    this.timeout(5000);
    var secret = "abcdef";
    hashpasslib.make_storeable(secret, function(storeable) {
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
    hashpasslib.check_stored(secret, stored, function(result) {
      expect(result).to.be(true);
      done();
    });
  });

  test("check_stored reject", function(done) {
    // Test with an 11 round bcrypt.
    var secret = "blowfish";
    // This stored hash does not match the secret.
    var stored = "$2y$11$Gzhmkebfiz2OapRqu/zwSOH2Wa9uAsbb4Vd5q3iKBILsMRX8MBpQa";
    hashpasslib.check_stored(secret, stored, function(result) {
      expect(result).to.be(false);
      done();
    });
  });

  test("check_stored reject fail", function(done) {
    // Test with an 11 round bcrypt.
    var secret = "blowfish";
    // This stored hash does not match the secret.
    var stored = "bogus";
    hashpasslib.check_stored(secret, stored, function(result) {
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
    this._test_site(0, this.intermediates[0], "ping0", "yAhnTfcJd#g3UpB7p3Fa");
    this._test_site(0, this.intermediates[1], "ping0", "Rsgdca3E9E(7KU=JMY3o");
    // 1 reroll.
    this._test_site(1, this.intermediates[0], "ping6", "s*t}?z8xzAAWd3#LSAcS");
    this._test_site(1, this.intermediates[1], "ping2", "5E)@{TRxkS=+WT=}N4sT");
  });

  test("make_site_password with more rerolls", function() {
    this._test_site(3, this.intermediates[0], "ping11", "m=vTw7@JhaYGmsF8p9qN");
    this._test_site(4, this.intermediates[0], "ping7956", "dEVK@9L@XQ?gr{59(pv?");
    this._test_site(6, this.intermediates[0], "ping166039", "HppQ3vP6ba)wLeG?YUBN");
    this._test_site(6, this.intermediates[0], "ping343496", "jGL+qAXTF4XG9fe39n=@");
  });
});

mocha.run();

}); // End of module.
