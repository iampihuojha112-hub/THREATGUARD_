"""Generate a synthetic smoke-test dataset (NOT a substitute for a real corpus).

    python datasets/generate_sample.py --rows 1600 --out datasets/sample_dataset.csv
"""
import argparse
import csv
import random

BRANDS = ["PayPal", "Microsoft", "Amazon", "Apple", "Netflix", "Chase", "DocuSign", "Dropbox", "FedEx", "LinkedIn"]
NAMES = ["Alex", "Priya", "Jordan", "Sam", "Maria", "Chen", "Lena", "Omar", "Riya", "Tom"]
PROJECTS = ["Q3 roadmap", "onboarding deck", "vendor review", "release checklist", "budget draft", "design handoff", "sprint retro"]
BAD_TLDS = ["xyz", "top", "click", "work", "tk", "icu"]

PHISH_SUBJECTS = [
    "Urgent: your {b} account has been suspended",
    "Action required: verify your {b} password",
    "Security alert: unusual sign-in to your {b} account",
    "Final notice: payment failed for your {b} subscription",
    "You have won a {b} gift card - claim now",
    "Invoice overdue - immediate payment required",
    "Confirm your identity to avoid account closure",
    "Your {b} package could not be delivered",
]
PHISH_BODIES = [
    "Dear customer, we detected unusual activity on your {b} account. Your account will be suspended within 24 hours unless you verify your identity. Click here to verify your account: {url}",
    "Your payment failed. Update your billing information immediately to avoid losing access. Log in to {url} and confirm your password and credit card details.",
    "Congratulations! You have won a prize. To claim your reward send your bank account and routing number or buy a gift card and reply with the code. Act now: {url}",
    "Final warning: your mailbox is full. Sign in to {url} and enter your password to re-activate your account. Failure to comply will result in permanent closure.",
    "We could not deliver your parcel. Pay a small customs fee at {url} using your credit card. This offer expires today, respond immediately.",
    "Attached is an overdue invoice. Please make a wire transfer to the account below as soon as possible. Legal action may follow. Confirm at {url}",
]
LEGIT_SUBJECTS = [
    "{p} - notes from today's meeting",
    "Re: {p}",
    "Lunch on Thursday?",
    "Your order has shipped",
    "Weekly team update",
    "Reminder: {p} review on Friday",
    "Thanks for your help with the {p}",
    "Receipt for your purchase",
]
LEGIT_BODIES = [
    "Hi {n}, thanks for joining the call. I have attached the notes for the {p}. Let me know if I missed anything and we can discuss it on Monday.",
    "Hey {n}, are you free for lunch on Thursday? There is a new place near the office. Happy to move it if the {p} review runs late.",
    "Hello {n}, your order #{num} has shipped and should arrive in three to five business days. You can track it from your account page. Thanks for shopping with us.",
    "Team, here is the weekly update. The {p} is on track, QA found two minor issues which are already fixed. Please review the document before our sync tomorrow.",
    "Hi {n}, I reviewed the {p} and left a few comments in the shared document. Overall it looks good. Could you update the numbers before we send it out?",
    "Thank you for your purchase. Your receipt is attached. If you have any questions about the invoice, reply to this email and our team will help.",
]


def phish_row(rng):
    b = rng.choice(BRANDS)
    url = rng.choice([
        f"http://{b.lower()}-secure-login.{rng.choice(BAD_TLDS)}/verify",
        f"http://{rng.randint(11, 220)}.{rng.randint(1, 250)}.{rng.randint(1, 250)}.{rng.randint(1, 250)}/login",
        "http://bit.ly/" + "".join(rng.choices("abcdefghijk123456", k=6)),
        f"http://{b.lower()}.account-update.{rng.choice(BAD_TLDS)}/",
    ])
    sender = rng.choice([
        f"{b.lower()}-support@{b.lower()}-alerts.{rng.choice(BAD_TLDS)}",
        f"security@{b.lower()}.verify-{rng.randint(100, 999)}.{rng.choice(BAD_TLDS)}",
        f"{b.lower()}.billing@gmail.com",
    ])
    return rng.choice(PHISH_SUBJECTS).format(b=b), sender, rng.choice(PHISH_BODIES).format(b=b, url=url), 1


def legit_row(rng):
    n, p = rng.choice(NAMES), rng.choice(PROJECTS)
    domain = rng.choice(["acme.com", "northwind.io", "example.org", "contoso.com", "initech.com"])
    sender = f"{rng.choice(NAMES).lower()}.{rng.choice(['k', 'm', 'r', 's'])}@{domain}"
    body = rng.choice(LEGIT_BODIES).format(n=n, p=p, num=rng.randint(10000, 99999))
    if rng.random() < 0.2:
        body += " Details: https://" + domain + "/docs/" + str(rng.randint(1, 500))
    return rng.choice(LEGIT_SUBJECTS).format(p=p), sender, body, 0


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--rows", type=int, default=1600)
    parser.add_argument("--out", default="datasets/sample_dataset.csv")
    parser.add_argument("--seed", type=int, default=7)
    args = parser.parse_args()
    rng = random.Random(args.seed)
    rows = [phish_row(rng) if i % 2 else legit_row(rng) for i in range(args.rows)]
    rng.shuffle(rows)
    with open(args.out, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["subject", "sender", "body", "label"])
        writer.writerows(rows)
    print(f"wrote {len(rows)} rows to {args.out}")


if __name__ == "__main__":
    main()
