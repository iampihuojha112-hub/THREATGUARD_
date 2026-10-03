import Link from "next/link";
import { DashboardPreview } from "@/components/landing/dashboard-preview";
import { HeroDemo } from "@/components/landing/hero-demo";
import { SiteFooter } from "@/components/landing/site-footer";
import { Logo } from "@/components/logo";
import { Button } from "@/components/ui/button";
import { SCAN_META } from "@/lib/scan-types";
import { createClient } from "@/lib/supabase/server";

const CHANNELS = [
  {
    type: "email" as const,
    examines: "Subject and body wording, the sender's domain compared with the brand it claims to be, and every link in the message.",
    finding: "Sender claims to be Microsoft but writes from a free mail address.",
  },
  {
    type: "url" as const,
    examines:
      "37 properties of the address itself: length, subdomain depth, hyphens and digits, IP hosts, shorteners, high-abuse extensions, brand names on the wrong domain and redirect parameters.",
    finding: "A bank's name sits in a subdomain of an unrelated .xyz domain.",
  },
  {
    type: "sms" as const,
    examines: "Message wording, embedded links, phone numbers and short codes, and requests for OTPs, KYC updates or delivery fees.",
    finding: "Courier notice asks for a small fee through a shortened link.",
  },
];

const STEPS = [
  { title: "Paste what you received", body: "An email with its sender, a bare URL, or the text of an SMS. Nothing is forwarded or opened." },
  { title: "Break it into signals", body: "Text is cleaned and weighted by TF-IDF. URLs become 37 numeric features. Links, numbers and amounts are normalised." },
  { title: "Score it", body: "The trained model returns a probability, shown as a 0 to 100 risk score with a confidence value." },
  { title: "See why, and keep the record", body: "Rule checks and the model's strongest terms explain the verdict. The scan is saved to your private history." },
];

const BENEFITS = [
  { title: "Reasons you can check", body: "Each verdict lists the sender details, links and phrases behind it, so you can decide whether you agree." },
  { title: "Private by default", body: "Scans belong to your account. Row-level security in the database stops other users from reading them." },
  { title: "Trained on your data", body: "Training pipelines for all three channels ship with the platform, so the models can match the scams you actually receive." },
  { title: "Nothing gets opened", body: "URLs are analysed as text. ThreatGuard never visits a link, so checking one cannot trigger anything." },
];

const MODEL_ROWS = [
  { channel: "Email", input: "Subject and body text", method: "TF-IDF with 1 to 2 word phrases" },
  { channel: "URL", input: "37 lexical features", method: "Log scaling for logistic regression, raw counts for trees" },
  { channel: "SMS", input: "Message text", method: "TF-IDF with link, phone, short-code and money tokens" },
];

export default async function Home() {
  const supabase = await createClient();
  const {
    data: { user },
  } = await supabase.auth.getUser();
  const primaryHref = user ? "/analyze" : "/register";

  return (
    <div className="min-h-screen">
      <header className="mx-auto flex max-w-6xl items-center justify-between px-5 py-5">
        <Logo />
        <nav aria-label="Sections" className="hidden items-center gap-6 text-sm text-muted-foreground md:flex">
          <a href="#detection" className="hover:text-foreground">Detection</a>
          <a href="#workflow" className="hover:text-foreground">How it works</a>
          <a href="#models" className="hover:text-foreground">Models</a>
          <a href="#dashboard" className="hover:text-foreground">Dashboard</a>
        </nav>
        <div className="flex items-center gap-2">
          {user ? (
            <Button asChild size="sm">
              <Link href="/dashboard">Open dashboard</Link>
            </Button>
          ) : (
            <>
              <Button asChild variant="ghost" size="sm">
                <Link href="/login">Sign in</Link>
              </Button>
              <Button asChild size="sm">
                <Link href="/register">Create account</Link>
              </Button>
            </>
          )}
        </div>
      </header>

      <main>
        {/* Hero */}
        <section className="mx-auto grid max-w-6xl items-center gap-12 px-5 pb-20 pt-10 lg:grid-cols-[1fr_1.05fr] lg:pt-16">
          <div>
            <p className="mb-5 inline-flex items-center gap-2 rounded-full border px-3 py-1 text-sm text-muted-foreground">
              <span className="h-1.5 w-1.5 rounded-full bg-safe" />
              AI-powered threat detection
            </p>
            <h1 className="text-4xl font-semibold leading-[1.08] tracking-tight sm:text-5xl lg:text-[3.4rem]">
              Know whether an email, link or text is a trap before you act on it.
            </h1>
            <p className="mt-6 max-w-xl text-lg leading-relaxed text-muted-foreground">
              ThreatGuard runs a separate machine-learning model for each channel and shows the sender details, links and phrases behind every verdict.
            </p>
            <div className="mt-8 flex flex-wrap gap-3">
              <Button asChild size="lg">
                <Link href={primaryHref}>{user ? "Analyze something" : "Create an account"}</Link>
              </Button>
              <Button asChild size="lg" variant="outline">
                <a href="#workflow">See how it works</a>
              </Button>
            </div>
          </div>
          <HeroDemo />
        </section>

        {/* Overview */}
        <section id="overview" className="border-t">
          <div className="mx-auto grid max-w-6xl gap-10 px-5 py-20 lg:grid-cols-[1fr_1.1fr]">
            <h2 className="text-3xl font-semibold leading-tight tracking-tight">One place to check anything suspicious that reaches your inbox or your phone.</h2>
            <div className="space-y-4 text-lg leading-relaxed text-muted-foreground">
              <p>
                Phishing rarely stays in one channel. A fake delivery notice arrives as a text, points to a look-alike domain, and is followed by an email asking you to confirm your card.
              </p>
              <p>
                ThreatGuard checks each piece with a model built for it, then keeps every result in one private history, so the patterns across email, URLs and SMS are easy to see.
              </p>
            </div>
          </div>
        </section>

        {/* Capabilities */}
        <section id="detection" className="border-t">
          <div className="mx-auto max-w-6xl px-5 py-20">
            <h2 className="max-w-2xl text-3xl font-semibold leading-tight tracking-tight">What it looks at in each kind of message</h2>
            <div className="mt-10 divide-y border-y">
              {CHANNELS.map(({ type, examines, finding }) => {
                const { label, icon: Icon } = SCAN_META[type];
                return (
                  <div key={type} className="grid gap-4 py-7 lg:grid-cols-[180px_1.5fr_1fr] lg:gap-10">
                    <div className="flex items-center gap-3 lg:items-start">
                      <span className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary/15 text-primary">
                        <Icon className="h-5 w-5" />
                      </span>
                      <h3 className="text-lg font-semibold">{label}</h3>
                    </div>
                    <p className="leading-relaxed text-foreground/85">{examines}</p>
                    <p className="border-l-2 border-primary/40 pl-4 text-sm italic leading-relaxed text-muted-foreground">{finding}</p>
                  </div>
                );
              })}
            </div>
          </div>
        </section>

        {/* Workflow */}
        <section id="workflow" className="border-t">
          <div className="mx-auto max-w-6xl px-5 py-20">
            <h2 className="max-w-2xl text-3xl font-semibold leading-tight tracking-tight">From paste to verdict in four steps</h2>
            <ol className="mt-12 grid gap-10 md:grid-cols-4 md:gap-6">
              {STEPS.map((step, i) => (
                <li key={step.title} className="relative md:pt-10">
                  <span className="mb-3 flex h-8 w-8 items-center justify-center rounded-full border border-primary/50 bg-primary/10 text-sm font-semibold text-primary md:absolute md:left-0 md:top-0 md:mb-0">
                    {i + 1}
                  </span>
                  {i < STEPS.length - 1 && <span aria-hidden="true" className="absolute left-[2.4rem] right-[-0.5rem] top-4 hidden border-t border-dashed border-border md:block" />}
                  <h3 className="font-semibold">{step.title}</h3>
                  <p className="mt-2 text-sm leading-relaxed text-muted-foreground">{step.body}</p>
                </li>
              ))}
            </ol>
          </div>
        </section>

        {/* AI & ML */}
        <section id="models" className="border-t">
          <div className="mx-auto grid max-w-6xl gap-12 px-5 py-20 lg:grid-cols-[1fr_1.15fr]">
            <div>
              <h2 className="text-3xl font-semibold leading-tight tracking-tight">Three models, each tuned to its own kind of message</h2>
              <p className="mt-5 leading-relaxed text-muted-foreground">
                Every channel is trained with logistic regression, random forest and XGBoost. The three are compared on held-out data, and the one with the best F1 score is the one that gets saved and used.
              </p>
              <p className="mt-4 leading-relaxed text-muted-foreground">
                The score always comes from the model. The rule checks that flag look-alike domains, shorteners and pressure phrases never change it. They exist so you can see why.
              </p>
            </div>
            <div className="space-y-5">
              <div className="overflow-x-auto rounded-lg border">
                <table className="w-full min-w-[460px] text-left text-sm">
                  <thead className="border-b bg-muted/40 text-muted-foreground">
                    <tr>
                      <th className="px-4 py-3 font-medium">Channel</th>
                      <th className="px-4 py-3 font-medium">Model input</th>
                      <th className="px-4 py-3 font-medium">Preparation</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y">
                    {MODEL_ROWS.map((r) => (
                      <tr key={r.channel}>
                        <td className="px-4 py-3 font-medium">{r.channel}</td>
                        <td className="px-4 py-3 text-muted-foreground">{r.input}</td>
                        <td className="px-4 py-3 text-muted-foreground">{r.method}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
              <div>
                <p className="mb-2 text-sm text-muted-foreground">Retraining on your own dataset is one command:</p>
                <pre className="overflow-x-auto rounded-lg border bg-background/70 p-4 font-mono text-sm text-foreground/90">
{`python train_url.py --data datasets/urls.csv
python train_sms.py --data datasets/sms.csv
python train.py     --data datasets/emails.csv`}
                </pre>
              </div>
            </div>
          </div>
        </section>

        {/* Dashboard preview */}
        <section id="dashboard" className="border-t">
          <div className="mx-auto max-w-6xl px-5 py-20">
            <div className="grid gap-6 lg:grid-cols-[1fr_1.1fr] lg:items-end">
              <h2 className="text-3xl font-semibold leading-tight tracking-tight">Your scan history turns into a picture of what is targeting you</h2>
              <p className="leading-relaxed text-muted-foreground">
                See how many emails, links and texts you have checked, how many were threats, and how risky they were. Filter the full history by type, verdict or search term.
              </p>
            </div>
            <div className="mt-10">
              <DashboardPreview />
            </div>
          </div>
        </section>

        {/* Benefits */}
        <section className="border-t">
          <div className="mx-auto max-w-6xl px-5 py-20">
            <h2 className="max-w-2xl text-3xl font-semibold leading-tight tracking-tight">Built to be trusted, not just fast</h2>
            <dl className="mt-10 grid gap-x-16 gap-y-10 md:grid-cols-2">
              {BENEFITS.map((b) => (
                <div key={b.title} className="border-t pt-5">
                  <dt className="text-lg font-semibold">{b.title}</dt>
                  <dd className="mt-2 leading-relaxed text-muted-foreground">{b.body}</dd>
                </div>
              ))}
            </dl>
          </div>
        </section>

        {/* CTA */}
        <section className="border-t">
          <div className="mx-auto flex max-w-6xl flex-col items-start justify-between gap-8 px-5 py-20 md:flex-row md:items-center">
            <div className="max-w-xl">
              <h2 className="text-3xl font-semibold leading-tight tracking-tight">Got something suspicious in front of you right now?</h2>
              <p className="mt-3 text-muted-foreground">Paste it in and get a verdict in a few seconds. Do not click the link first.</p>
            </div>
            <div className="flex flex-wrap gap-3">
              <Button asChild size="lg">
                <Link href={primaryHref}>{user ? "Analyze something" : "Create an account"}</Link>
              </Button>
              {!user && (
                <Button asChild size="lg" variant="outline">
                  <Link href="/login">Sign in</Link>
                </Button>
              )}
            </div>
          </div>
        </section>
      </main>

      <SiteFooter />
    </div>
  );
}
