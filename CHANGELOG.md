# Changelog

<!--next-version-placeholder-->

## v1.2.0 (2020-11-25)
### Feature
* Only show reply keyboard when needed ([`06760a3`](https://github.com/hokus15/melib-telegram-bot/commit/06760a3d1d83ece33351115db7690d953b6bb7a7))
* Add lista and libres commands ([`3da581c`](https://github.com/hokus15/melib-telegram-bot/commit/3da581c247c4ecea334e4397f3210866e5174e19))

### Fix
* Changes in texts returned by the bot and better error handling ([`f138dbd`](https://github.com/hokus15/melib-telegram-bot/commit/f138dbd75874dec297104bfeee12e9db75a02982))
* IF any text is sent to the bot, it will look for free chargers ([`b887132`](https://github.com/hokus15/melib-telegram-bot/commit/b887132f15955215c6c34c5b38cd3772d0bb279b))
* Pop onlyAvailable info instead of getting it ([`9a68c98`](https://github.com/hokus15/melib-telegram-bot/commit/9a68c98c360f5770e675543f3b8f68eca8c3892a))
* Remove reply keyboard when not needed ([`e6ef39b`](https://github.com/hokus15/melib-telegram-bot/commit/e6ef39b8f0c41046aa7a14af3b346e2ee205d9bb))
* Conversation tests ([`0a71919`](https://github.com/hokus15/melib-telegram-bot/commit/0a7191933aaca14d4d9843bdc80e95f334b21933))
* Added needed charger statuses ([`a0e1833`](https://github.com/hokus15/melib-telegram-bot/commit/a0e18334fcce034ab7cbf9ff7bf31b47d3f46753))
* Debugging ([`ca4287c`](https://github.com/hokus15/melib-telegram-bot/commit/ca4287c6105d1e7e279137506b0ff9b81310fc70))
* Added command buttons to reply keyboard ([`804fb68`](https://github.com/hokus15/melib-telegram-bot/commit/804fb68885bcec8deb077068a7b8971f39419944))
* Inlcude offline chargers ([`976c8ec`](https://github.com/hokus15/melib-telegram-bot/commit/976c8ecc8d8fae1ad17e3ff0814e556ddab3fe44))
* Fix fallback method ([`7300b41`](https://github.com/hokus15/melib-telegram-bot/commit/7300b411b07dead8a140f2124cdfdba19491a87a))
* Markup errors in text ([`3d7716a`](https://github.com/hokus15/melib-telegram-bot/commit/3d7716ac2c59e9a3d7fb06a3759b18eba43de84a))
* Fix map link ([`53a01ff`](https://github.com/hokus15/melib-telegram-bot/commit/53a01ffcc044af9b86d1c609c0e3498bfd58a3fb))
* Texts corrections ([`40323d0`](https://github.com/hokus15/melib-telegram-bot/commit/40323d0d9abdbece62ba5cc62717fc38bf279139))
* Fix unit tests ([`5cf17fb`](https://github.com/hokus15/melib-telegram-bot/commit/5cf17fbb6cc998dc5651e3fa4c20f0ad0b6646d1))
* Change parse mode to HTML ([`677cd62`](https://github.com/hokus15/melib-telegram-bot/commit/677cd6254058834561ce379598b96cd71b4cdd94))
* Escape markdown ([`7fd0a03`](https://github.com/hokus15/melib-telegram-bot/commit/7fd0a03f0e92eb28ae40bf483f19e2c8cd65940e))
* Fix misspelling ([`3e4cb9a`](https://github.com/hokus15/melib-telegram-bot/commit/3e4cb9abb7852f48ecc5defd6ecf25605b060a04))

## v1.1.0 (2020-11-19)
### Feature
* Add ADMIN_USER as a env variable instead of taking the first user in VALID_USERS as admin ([`3bc5f4b`](https://github.com/hokus15/melib-telegram-bot/commit/3bc5f4b6c74ea74a1a6b93fa0d632774eecc2337))

### Fix
* Changelog in english ([`ad0aa4b`](https://github.com/hokus15/melib-telegram-bot/commit/ad0aa4b4adb4654291426fafecab53628d4867b9))
* Improve readability of welcome message. ([`08a52b2`](https://github.com/hokus15/melib-telegram-bot/commit/08a52b28af5a31d9437ea9db60fd358ee9786abd))
* Improve messages returned to users ([`fedfa30`](https://github.com/hokus15/melib-telegram-bot/commit/fedfa305265636243195eb6577d3a4fb4d2c411b))
* Fix test ([`e5a9230`](https://github.com/hokus15/melib-telegram-bot/commit/e5a92306fe81f8db550dca73e6402899399b3bbe))
* Fix misspelling in some messages ([`f2e999e`](https://github.com/hokus15/melib-telegram-bot/commit/f2e999e3214fd92990853fe85aff9b8542e84814))
* If no ADMIN_USER env variable has been defined it takes the first user from VALID_USERS as the ADMIN_USER ([`526a401`](https://github.com/hokus15/melib-telegram-bot/commit/526a401ed7234cc5954f0a494ade062b2142c50a))
* Remove date from logging ([`d4c0133`](https://github.com/hokus15/melib-telegram-bot/commit/d4c0133f2b3a903f77d8955a2218b999b780daa8))
* Update method and conversation status names ([`2cf8a2f`](https://github.com/hokus15/melib-telegram-bot/commit/2cf8a2f4469dcf87c0831eaf96559790a51a6ad9))
* Add some logs ([`070484b`](https://github.com/hokus15/melib-telegram-bot/commit/070484b418fac009d7a70dc70be944ecaf83b6c0))

## v1.0.0 (2020-11-12)
### Feature
* Remove Google Cloud Functions support ([`bede341`](https://github.com/hokus15/melib-telegram-bot/commit/bede341705e108f21c3901a9e07e7084e1365a9a))

### Breaking
* With this change the bot will not be able to be  deployed anymore as a Google Cloud Function  ([`bede341`](https://github.com/hokus15/melib-telegram-bot/commit/bede341705e108f21c3901a9e07e7084e1365a9a))

## v0.7.0 (2020-11-11)
### Feature
* Documentation update ([`874d76e`](https://github.com/hokus15/melib-telegram-bot/commit/874d76ec58a9966b1b20700cfe9713817ca5e021))
* Add app.json ([`86e0951`](https://github.com/hokus15/melib-telegram-bot/commit/86e0951ee3a6769426704f9362e5cceb043e6ffd))

### Fix
* Add new env variable to app.json ([`bf67f23`](https://github.com/hokus15/melib-telegram-bot/commit/bf67f23a021f36aaf6bc3b5d94118fa6d868ed59))
* Moooooore docuemtation updates ([`7875d52`](https://github.com/hokus15/melib-telegram-bot/commit/7875d526f4fff0e27d5eef7d7e3bd0cd8ba9a8f9))
* Documentation update ([`9e9bef3`](https://github.com/hokus15/melib-telegram-bot/commit/9e9bef3bccf0135522eddb677d674fc928d99393))
* Better description app.son descriptions ([`2092258`](https://github.com/hokus15/melib-telegram-bot/commit/20922580c52f845b9b2f62bf48446ccce11fb53b))
* Skip conversation tests on non windows environments ([`2178072`](https://github.com/hokus15/melib-telegram-bot/commit/21780722381c008bc4f531473677439aa2e7426f))
* Fix app.json ([`4847dc3`](https://github.com/hokus15/melib-telegram-bot/commit/4847dc3ad701168372c199be5c247e7f10504ad2))

## v0.6.0 (2020-11-11)
### Feature
* Refactor heroku bot ([`f3437bb`](https://github.com/hokus15/melib-telegram-bot/commit/f3437bb060aff2bfdc4732b2e84a049c128941ec))

### Fix
* Added needed changes to be able to run bot in heroku ([`f1b66db`](https://github.com/hokus15/melib-telegram-bot/commit/f1b66dbf3c8db6c9facbeb41e5980e6d90a8d386))
* Fix error executing bot on heroku ([`5c1f989`](https://github.com/hokus15/melib-telegram-bot/commit/5c1f989a3bcf630c630b559de6126b0a632813b1))

## v0.5.1 (2020-11-10)
### Fix
* Fix requirements.txt to work with Google Cloud ([`6d4a5cf`](https://github.com/hokus15/melib-telegram-bot/commit/6d4a5cf00007d840b2a3ba3af830b2b7323f107e))

## v0.5.0 (2020-11-10)
### Feature
* Add some logging ([`f6f62b0`](https://github.com/hokus15/melib-telegram-bot/commit/f6f62b0fa305b78d34efd90b47453140b46d524d))
* Refactor to deploy on heroku ([`3fc22bf`](https://github.com/hokus15/melib-telegram-bot/commit/3fc22bfd920361fb9171cbcede39dba50a9b84e0))
* Start heroku refactor ([`65c4343`](https://github.com/hokus15/melib-telegram-bot/commit/65c4343c63bf27e38085d209d830139dd253631c))

### Fix
* Semantic version config ([`7c7ae34`](https://github.com/hokus15/melib-telegram-bot/commit/7c7ae344a9e0d4da9db1be13c5b1113b542f9e1c))
* Fix dependencies ([`d2932e6`](https://github.com/hokus15/melib-telegram-bot/commit/d2932e6ac259483510271d1dd623f81f2bbb2197))
* Add print for debug ([`47006d2`](https://github.com/hokus15/melib-telegram-bot/commit/47006d200cda95b438dece96370c733e2326bcd3))
* Fix import ([`7ee75c3`](https://github.com/hokus15/melib-telegram-bot/commit/7ee75c302b243f9bccd8beb4466ea701dd4e95a6))
* Fix melib import ([`552a5b3`](https://github.com/hokus15/melib-telegram-bot/commit/552a5b3bd224fa31cd128347c75c84fbd372f9fe))
* Added requirements ([`678375c`](https://github.com/hokus15/melib-telegram-bot/commit/678375c32b4d61ac6877e3b1abe70cdf19935d19))

## v0.4.1 (2020-11-08)
### Fix
* Code style ([`3cac2d1`](https://github.com/hokus15/melib-telegram-bot/commit/3cac2d136c8d3ad1f22e07fa90c6dbae8f5bc247))
* Fix warning thrown in unit tests ([`3b7e3ec`](https://github.com/hokus15/melib-telegram-bot/commit/3b7e3ec5959729c236a34ae93a5404e27462a5f8))

## v0.4.0 (2020-11-03)
### Feature
* Include bot version in help message ([`ab53a22`](https://github.com/hokus15/melib-telegram-bot/commit/ab53a22dff809fadb566b31a47291a181dbf70a1))

### Fix
* Avoid to updload unneeded files to Cloud Functions ([`fbfb80d`](https://github.com/hokus15/melib-telegram-bot/commit/fbfb80d4f26d579af54fa4569ec915030cb4959b))

## v0.3.0 (2020-11-03)
### Feature
* Use semver ([`aae272c`](https://github.com/hokus15/melib-telegram-bot/commit/aae272cfc06cd2b5ea2ce55089c3ab52bf846207))
* Use semver ([`df8f325`](https://github.com/hokus15/melib-telegram-bot/commit/df8f3253ddb1271dd7806e4292d41da6099b843e))

### Fix
* Fix semver ([`1e78940`](https://github.com/hokus15/melib-telegram-bot/commit/1e78940b44cf3d66bc0ac17d9fd8aae09439ac80))
