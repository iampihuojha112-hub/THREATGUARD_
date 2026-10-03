"""Generate tiny synthetic SMS and URL datasets for smoke-testing the pipelines (NOT real training data).

    python datasets/generate_sample_sms_url.py --out-dir datasets
"""
import argparse
import csv
import os
import random

SCAM_SMS = [
    "WINNER!! You have won a {n} prize. Call {p} now to claim. Reply STOP to opt out",
    "URGENT: your bank account is suspended. Verify your KYC at {u} within 24 hours",
    "Your parcel could not be delivered. Pay a small fee at {u} to reschedule delivery",
    "Congratulations! You are selected for a free gift voucher. Claim now {u}",
    "Your OTP is {c}. Do not share. If this was not you, confirm your card number at {u}",
    "FREE entry to our weekly draw! Text WIN to {c} to claim your cash reward",
]
LEGIT_SMS = [
    "Hey, are we still on for dinner at {t}?",
    "Your appointment with Dr. Rao is confirmed for tomorrow at {t}.",
    "Running late, will reach in {m} minutes. Start without me",
    "Thanks for your payment. Your receipt number is {c}.",
    "Can you send me the notes from today's class?",
    "Your cab is arriving in {m} minutes. Driver will call you.",
]
BRANDS = ["paypal", "amazon", "hdfc", "microsoft", "netflix", "apple"]
BAD_TLDS = ["xyz", "top", "tk", "click", "icu"]
GOOD_SITES = ["github.com/{w}", "en.wikipedia.org/wiki/{w}", "www.bbc.co.uk/news/{w}", "docs.python.org/3/library/{w}.html",
              "stackoverflow.com/questions/{n}/{w}", "www.nytimes.com/2025/{n}/{w}.html", "news.ycombinator.com/item?id={n}"]
WORDS = ["python", "weather", "recipe", "travel", "science", "history", "budget", "garden", "music", "design"]


FILLER = ["today", "please", "asap", "tonight", "this week", "dear customer", "hello", "hi there", "friend", "team", "sir",
          "again", "soon", "okay", "thanks", "regards", "kindly", "note", "info", "update", "offer", "alert"]


def sms_row(rng, label):
    u = rng.choice([f"http://bit.ly/{rng.randint(1000, 99999)}", f"http://secure-{rng.choice(BRANDS)}.{rng.choice(BAD_TLDS)}/v", f"http://{rng.randint(11, 220)}.{rng.randint(1, 250)}.4.9/x"])
    fill = dict(n=rng.choice(["$1000", "Rs 50000", "£900"]), p=f"0906{rng.randint(1000000, 9999999)}", u=u, c=rng.randint(10000, 999999),
                t=f"{rng.randint(1, 11)}pm", m=rng.randint(2, 30))
    text = rng.choice(SCAM_SMS if label else LEGIT_SMS).format(**fill)
    extra = " ".join(rng.choices(FILLER, k=rng.randint(1, 4)))
    return (f"{extra} {text}" if rng.random() < 0.5 else f"{text} {extra}"), label


def url_row(rng, label):
    if not label:
        return "https://" + rng.choice(GOOD_SITES).format(w=rng.choice(WORDS), n=rng.randint(100, 99999)), 0
    b = rng.choice(BRANDS)
    return rng.choice([
        f"http://{b}-secure-login.{rng.choice(BAD_TLDS)}/verify/account?id={rng.randint(1, 9999)}",
        f"http://{rng.randint(11, 220)}.{rng.randint(1, 250)}.{rng.randint(1, 250)}.{rng.randint(1, 250)}/{b}/signin.php",
        f"http://{b}.account-update-{rng.randint(10, 99)}.{rng.choice(BAD_TLDS)}/webscr?cmd=login&redirect=http://evil.{rng.choice(BAD_TLDS)}",
        f"http://bit.ly/{''.join(rng.choices('abcdef123456', k=6))}",
        f"http://free-{rng.choice(WORDS)}-download.{rng.choice(BAD_TLDS)}/setup{rng.randint(1, 99)}.exe",
    ]), 1


def write(path, header, rows):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(rows)
    print(f"wrote {len(rows)} rows to {path}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", default="datasets")
    ap.add_argument("--rows", type=int, default=1200)
    ap.add_argument("--seed", type=int, default=11)
    a = ap.parse_args()
    rng = random.Random(a.seed)
    write(os.path.join(a.out_dir, "sample_sms.csv"), ["message", "label"], [sms_row(rng, i % 2) for i in range(a.rows)])
    write(os.path.join(a.out_dir, "sample_urls.csv"), ["url", "label"], [url_row(rng, i % 2) for i in range(a.rows)])


if __name__ == "__main__":
    main()
