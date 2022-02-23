from os import environ
from dotenv import load_dotenv

load_dotenv()

welcome = """Hey %s! Welcome to the Official {0} Airdrop 🤝

I would be guiding you throughout this process, follow the steps below.

1️⃣ Click the Join Airdrop button to perform the airdrop tasks and submit your information by clicking 'Register' button.

2️⃣ You can check your balance and get your referral link by using the My Balance button.

3️⃣ Please make sure that you have read the Information section.

""".format(environ.get('SYMBOL'))

captcha = """PROVE YOU ARE HUMAN

%s"""

captcha_fail = "🆘 Wrong\nGenerating New Equation"
captcha_success = "VERIFIED!"

success = "%s SAVED!"

newRef = """New user joined using your referral link

Total referral is %d"""

ENDED = """*AIRDROP HAS ENDED*"""

joining = """
💻 Please perform the {0} Airdrop tasks to earn up to 100,000 ${1} Tokens

💠 Join {0} [Telegram group](https://t.me/%s) & [Telegram channel](https://t.me/%s) (Required » 50,000 ${1})

💠 Follow {0} on [Twitter](https://twitter.com/%s) and retweet the [pinned post]({2}) by tagging 5 of your friends. (Required » 50,000 ${1})

Our airdrop task is as easy as it can be.""".format(environ.get("P_NAME"), environ.get("SYMBOL"), environ.get("PINNED_TWEET_URL"))

forceReg = """🆘 You can't register.

You must join [Telegram group](https://t.me/%s) `AND` [Telegram channel](https://t.me/%s) to proceed"""

bep20 = "📝 Please type your BEP-20 (Binance Smart Chain) wallet address (For instance: 0x.........)"
wrong_bep20 = "Please enter a valid BEP20 address (e.g 0x........)"

twitter_username_text = "📝 Please enter your Twitter username below (For instance: @{0})".format(
    environ.get("TWITTER_HANDLE"))
wrong_twitter_username = "Please enter a valid Twitter username (e.g @.{0})".format(
    environ.get("TWITTER_HANDLE"))

twitter_retweet_link_text = "📝 Please enter the link to your retweet (For instance: {0})".format(
    environ.get("PINNED_TWEET_URL"))

end = """🤝 Well done! Thank you for being a part of Token project!

You can use your referral link to invite more people to our airdrop.

👨‍👩‍👧 https://t.me/%s?start=%d

🗞 Note : ♻️ You can change your registration details by sending any of these commands:

1. /update_username -> to update your twitter's username
2. /update_link -> to update your twitter's retweet link
3. /update_bep20 -> to update your BEP20's address
"""

balance_text = """🏆 Referral Reward: %d ${0}
🏆 Completed Tasks Reward: 100,000 ${0}

👨‍👩‍👧 Number of Referral: %d (5,000 per referral)
\n
Referral Link♾ https://t.me/%s?start=%d""".format(environ.get("SYMBOL"))

info = """%s🔐 Subscribers who unfollow the mandatory social media tasks will not be eligible.

👨‍👩‍👧 Earn 5,000 ${0} extra rewards with the confirmed referrals.

⏳ Distribution date: Airdrop rewards will be distributed within 2 months after the end of the airdrop.
\n
♻️ You can change your registration details by sending any of these commands:

1. /update_username -> to update your twitter's username
2. /update_link -> to update your twitter's retweet link
3. /update_bep20 -> to update your BEP20's address

Referral Link♾ https://t.me/%s?start=%d""".format(environ.get("SYMBOL"))
