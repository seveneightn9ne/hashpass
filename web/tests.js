require(["./hashpasslib"], function(hashpasslib) { // Start of module.

mocha.setup('tdd');
mocha.checkLeaks();
mocha.run();

suite("HashPassAlg", function() {
  setup(function() {
    this.intermediates = [
      "$2b$13$X5A4.IjQghzyTGwc0wgRrebu3hlW/WFyN5GnvrTKvYsJtdsr5DXC6",
      "$2b$13$X5A4.IjQghzyTGwc0wgRrejiTwszgBLaN3PTew0gRtIrzb5EHsZB2"];

    this._test_site = function(rerolls, intermediate, slug, expected, done) {
      // Test one site password, ignores the reroll parameter.
      hashpasslib.make_password(intermediate, slug, function(result) {
        expect(expected).to.equal(result);
        done();
      });
    };
  });

  test("make_intermediate", function(done) {
    hashpasslib.make_intermediate("12342", function(result) {
      expect(result).to.equal("$2b$13$X5A4.IjQghzyTGwc0wgRrecUMeNiIgapq6zxM07dr3UDDdHUYWLTC");
    });
  });
  test("make_intermediate", function(done) {
    hashpasslib.make_intermediate("super secret", function(result) {
      expect(result).to.equal("$2b$13$X5A4.IjQghzyTGwc0wgRrejDmecj5/NNmPPb5ok4tXNuhs/rdP5zy");
    });
  });
  test("make_intermediate", function(done) {
    hashpasslib.make_intermediate("blowfish", function(result) {
      expect(result).to.equal("$2b$13$X5A4.IjQghzyTGwc0wgRrezL8JE8j/mpXN/V6YXoldoca002NMb0a");
    });
  });

  test("is_good_pass", function() {
    expect(hashpasslib.is_good_pass("a4#aaaaaaaaaaaaaaaaa")).to.be(true);
    expect(hashpasslib.is_good_pass("oooo6o#ooaaaaaaaaaaa")).to.be(true);
    expect(hashpasslib.is_good_pass("")).to.be(false);
    expect(hashpasslib.is_good_pass("oeuoeuOOO2343")).to.be(false);
  });

  test("make_storeable", function(done) {
    var secret = "abcdef";
    hashpasslib.make_storeable(secret, function(stored) {
      expect(result).to.be.equal(bcrypt.hashpw(secret, stored) == stored)
      done();
    });
  });

  test("check_stored accept", function(done) {
    // Test with an 11 round bcrypt.
    var secret = "blowfish";
    var stored = "$2b$11$Gzhmkebfiz2OapRqu/zWSOH2Wa9uAsbb4Vd5q3iKBILsMRX8MBpQa";
    alg.check_stored(secret, stored, function(result) {
      expect(result).to.be(true);
      done();
    });
  });

  test("check_stored reject", function(done) {
    // Test with an 11 round bcrypt.
    var secret = "blowfish";
    var stored = "$2b$11$Gzhmkebfiz2OapRqu/zWSOH2Wa9uAsbb4Vd5q3iKBILsMRX8MBpQa";
    alg.check_stored(secret, stored.substring(0, stored.length-1), function(result) {
      expect(result).to.be(false);
      done();
    });
  });

  test("bytes_to_pw_chars", function() {
    expect(hashpasslib._bytes_to_pw_chars([0, 0, 0])).to.equal("aaaa");
    expect(hashpasslib._bytes_to_pw_chars([255, 255, 255])).to.equal("????");
    expect(hashpasslib._bytes_to_pw_chars([4,32,196])).to.equal("bcde");
  });

  test("make_site_password with 0 rerolls", function(done) {
    this._test_site(0, self.intermediates[0], "b", "?T7}LNgNP)KkEYRATQ6m", done);
  });
  test("make_site_password with 0 rerolls", function(done) {
    this._test_site(0, self.intermediates[1], "b", "DuR49nd4W7@fEyH)M?Xk", done);
  });

  test("make_site_password with 1 reroll", function(done) {
    this._test_site(0, self.intermediates[0], "blunderbus40", "frP}JsfQXxjp5FTt}y{k", done);
  });
  test("make_site_password with 1 reroll", function(done) {
    this._test_site(0, self.intermediates[1], "sportsball", "NquDtLpKUhSRS7TgBY}f", done);
  });

  test("make_site_password with 3 rerolls", function(done) {
    this._test_site(0, self.intermediates[0], "blunderbus67555", "q7=s(}5nFgQEr8}JXoxv", done);
  });
  test("make_site_password with 4 rerolls", function(done) {
    this._test_site(0, self.intermediates[0], "blunderbus67679", "3dfdqnu@YfBGx)}*ByQ3", done);
  });
  test("make_site_password with 6 rerolls", function(done) {
    this._test_site(0, self.intermediates[0], "blunderbus403936", "V5Wuv?4kG*(?X)bpw?}V", done);
  });
  test("make_site_password with 6 rerolls", function(done) {
    this._test_site(0, self.intermediates[0], "blunderbus463867", "TDpxs?Fs#5SQ5*rCX#=z", done);
  });
});

mocha.run();

}); // End of module.
