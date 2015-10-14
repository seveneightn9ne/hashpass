# Password Manifesto
hashpass is a utility that implements a secure scheme for generating passwords.

This is my attempt at implementing the *optimal* password scheme.

## What makes a good password?
* *High entropy.* Long passwords with a broad charset have higher entropy. Also,
  they should not contain dictionary words or personal information. This makes
  them harder to crack by brute force.
* *Unique.* A different password should be used for everything, so that revealing
  one doesn't compromise any other.
* *Non compromising.* If someone sees one of your passwords, it should not give
  them information about how to generate any other passwords. e.g. if your Amazon
  password is `amazon*i<OyfG$`, then your google password is probably
  `google*i<0yfG$`, or at least `google` followed by 8 characters. This defeats
  the purpose of having a unique password between the two sites.

Here, I use *password scheme* to mean the way you choose your passwords.

## What makes a good password scheme?
* *Produces good passwords* according to the above criteria.
* *Requires little memorization.* The more you have to remember the more likely
  you are to cut corners.
* *Follows Kerckhoff's principle.* That is, the system should be secure even if
  everything about the system, except the key, is public knowledge.
* *Available anywhere.* I don't want to have to install LastPass before I can
  even log in to my Google account on a new computer. Given a new device, I should
  have my passwords with minimal setup, using only the information I keep in my head.

  Orignally I thought that this meant using only available-everywhere schemes, such
  as a common hashing algorithm. However, usually when you need a password you are also
  connected to the internet. So I think it's ok to have something available online
  that you can use (as long as that doesn't compromise security).

## The scheme
* You have a secret key, which is a Good Password (long and random). You have
  to memorize this but this is the only thing you have to memorize. It is the
  only thing keeping your system secure so KEEP IT SECRET. Never use it anywhere
  else. If you'd like to generate one now, you can do so with the following
  command:

  ```
  $ cat /dev/urandom | tr -dc 'a-zA-Z0-9-_!@#$%^&*()_+{}|:<>?=' | fold -w 20 | head -n 1
  ```

  I personally would say it's safe to write it down on paper and save it in your
  wallet until you're sure you've memorized it. Some more paranoid than me might
  disagree. You may also want to write it down and put it in a safe place in case
  of emergencies or amnesia.
* There is a unique component to every password which is obvious to you. For
  example, for a password for a website, the unique component can be the domain
  name. It doesn't have to be secure, it just has to be unique and obvious (so
  you'll never wonder what you picked).
* **Your password for a given service will be deterministically generated using only
  a combination of your secret key and the unique component.** HashPass produces a
  20 character password that contains a letter, a number, and a symbol.

## How does the algorithm work?
* It takes your master password, and runs it through a key derivation function. That is basically
  a very slow one-way function, making it infeasable to ever find your master given the output.
* It combines the result with your slug, and hashes it with SHA256. Now you have some random looking
  data that was deterministically generated.
* It maps those bytes into a 64-character charset made of uppercase, lowercase, numbers, and symbols.
* It takes the first 20 characters of that, and checks if it's a good password (Does it contain one
  of each type of character?
* If it's not a good password, it re-hashes the hash output and tries the same thing on that, until
  it finds a good password.

## What else does HashPass do?
* It makes sure your secret key isn't stored anywhere. You type it into a
  password input so it never appears on the screen.
* It saves the salted sha512 hash of your secret key on your computer to check for
  typos. Otherwise, there'd be no way to tell if you had typed your secret key
  correctly, and then you'd have a password you could never reproduce.
* It sends the password directly to your clipboard.

## Notes
* Chrome might store your passwords in plaintext (at least, you can look at them at any time).
  You may consider not letting chrome save your passwords.
* Some websites may require fewer characters or disallow symbols or have other requirements
  that this scheme violates. I haven't thought of a good solution for this. My current solution
  is simply to manually remove the invalid characters. I also save all my passwords in `pass`.
