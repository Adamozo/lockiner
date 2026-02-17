<script setup lang="ts">
definePageMeta({
  layout: false,
});

useSeoMeta({
  title: "Privacy Policy - LockIner",
  description: "LockIner privacy policy and data protection information",
});
</script>

<template>
  <div class="min-h-screen bg-background-black">
    <LandingNav />

    <div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
      <h1 class="text-3xl font-bold text-pure-white mb-2">Privacy Policy</h1>
      <p class="text-pure-white/40 text-sm mb-10">
        Last updated: February 17, 2026
      </p>

      <div class="space-y-8 text-pure-white/70 text-sm leading-relaxed">
        <!-- 1. Data Controller -->
        <section>
          <h2 class="text-xl font-semibold text-pure-white mb-3">
            1. Data Controller
          </h2>
          <p>
            The controller of your personal data is
            <strong class="text-pure-white"
              >MAKE IT REMOTE Adam Naworski</strong
            >, a sole proprietorship registered in the Central Register and
            Information on Economic Activity (CEIDG) of the Republic of Poland.
          </p>
          <ul class="mt-3 space-y-1 list-disc list-inside text-pure-white/60">
            <li>
              <strong class="text-pure-white/70">Address:</strong> ul. Jodlowa
              40/22, 55-200 Olawa, Poland
            </li>
            <li>
              <strong class="text-pure-white/70">NIP (Tax ID):</strong>
              9121950969
            </li>
            <li>
              <strong class="text-pure-white/70">REGON:</strong> 542153497
            </li>
          </ul>
          <p class="mt-3">
            For any data protection inquiries, you may contact us by using the
            contact details published on the platform or via the official CEIDG
            registry entry.
          </p>
        </section>

        <!-- 2. Alpha Release Notice -->
        <section
          class="border border-warning-orange/30 bg-warning-orange/5 rounded-lg p-5"
        >
          <h2 class="text-xl font-semibold text-warning-orange mb-3">
            2. Alpha Release Notice
          </h2>
          <p>
            LockIner is currently in
            <strong class="text-warning-orange">alpha release</strong>.
            Registration is available exclusively to invited users who possess a
            valid voucher code. The platform is under active development, and
            features, data structures, and policies may change. We will notify
            registered users of any material changes to this privacy policy.
          </p>
        </section>

        <!-- 3. Data We Collect -->
        <section>
          <h2 class="text-xl font-semibold text-pure-white mb-3">
            3. Personal Data We Collect
          </h2>
          <p>During registration we collect the following information:</p>
          <ul class="mt-3 space-y-2 list-disc list-inside">
            <li>
              <strong class="text-pure-white">Display name</strong> &mdash; a
              name or nickname you choose to identify yourself on the platform.
              <span class="text-warning-orange"
                >We strongly recommend using a nickname or first name only,
                rather than your full legal name.</span
              >
              The display name is visible to other members of your household.
            </li>
            <li>
              <strong class="text-pure-white">Email address</strong> &mdash;
              used solely for account verification purposes.
              <strong class="text-pure-white"
                >Your email address is stored exclusively in an irreversibly
                hashed (SHA-256) format.</strong
              >
              This means the platform cannot read, display, send emails to, or
              otherwise use your email address in any way. The hash is used only
              to verify that you are the owner of a given account when you
              manually type your email address during login. No one &mdash;
              including the platform administrators &mdash; can recover or access
              your original email address from the stored hash.
            </li>
            <li>
              <strong class="text-pure-white">Password</strong> &mdash; stored
              in a securely hashed format using the bcrypt algorithm. Your
              plaintext password is never stored.
            </li>
            <li>
              <strong class="text-pure-white">Voucher code</strong> &mdash; the
              invitation code used during registration, stored to track
              invitation usage.
            </li>
          </ul>
        </section>

        <!-- 4. Data Generated Through Usage -->
        <section>
          <h2 class="text-xl font-semibold text-pure-white mb-3">
            4. Data Generated Through Usage
          </h2>
          <p>
            As you use the platform, the following data may be created and
            stored:
          </p>
          <ul class="mt-3 space-y-1 list-disc list-inside">
            <li>
              Financial records (transactions, receipts, budgets, categories)
            </li>
            <li>Fitness data (workouts, exercises, weight measurements)</li>
            <li>Food and recipe information</li>
            <li>Journal entries</li>
            <li>Skills and learning progress</li>
            <li>Household membership and shared data</li>
          </ul>
          <p class="mt-3">
            All usage data is associated with your account and is stored on
            servers located within the European Union.
          </p>
        </section>

        <!-- 5. Legal Basis -->
        <section>
          <h2 class="text-xl font-semibold text-pure-white mb-3">
            5. Legal Basis for Processing (GDPR Art. 6)
          </h2>
          <ul class="mt-2 space-y-2 list-disc list-inside">
            <li>
              <strong class="text-pure-white"
                >Performance of a contract (Art. 6(1)(b))</strong
              >
              &mdash; processing is necessary to provide the services you
              registered for, including account authentication, data storage, and
              household features.
            </li>
            <li>
              <strong class="text-pure-white"
                >Legitimate interest (Art. 6(1)(f))</strong
              >
              &mdash; we process minimal technical data (cookies for
              authentication and UI preferences) to ensure the platform functions
              correctly and securely.
            </li>
          </ul>
        </section>

        <!-- 6. Cookies -->
        <section>
          <h2 class="text-xl font-semibold text-pure-white mb-3">
            6. Cookies and Local Storage
          </h2>
          <p>
            LockIner uses only strictly necessary cookies. We do
            <strong class="text-pure-white">not</strong> use any third-party
            tracking, analytics, or advertising cookies.
          </p>
          <div class="mt-4 overflow-x-auto">
            <table class="w-full text-left text-sm">
              <thead>
                <tr class="border-b border-border-gray text-pure-white">
                  <th class="pb-2 pr-4">Cookie Name</th>
                  <th class="pb-2 pr-4">Purpose</th>
                  <th class="pb-2 pr-4">Duration</th>
                  <th class="pb-2">Type</th>
                </tr>
              </thead>
              <tbody class="text-pure-white/60">
                <tr class="border-b border-border-gray/30">
                  <td class="py-2 pr-4 font-mono text-xs">
                    scrooge_access_token
                  </td>
                  <td class="py-2 pr-4">
                    Authentication token (JWT) to keep you logged in
                  </td>
                  <td class="py-2 pr-4">30 minutes</td>
                  <td class="py-2">Strictly necessary</td>
                </tr>
                <tr class="border-b border-border-gray/30">
                  <td class="py-2 pr-4 font-mono text-xs">
                    scrooge_refresh_token
                  </td>
                  <td class="py-2 pr-4">
                    Token used to renew your session without re-entering
                    credentials
                  </td>
                  <td class="py-2 pr-4">7 days</td>
                  <td class="py-2">Strictly necessary</td>
                </tr>
                <tr class="border-b border-border-gray/30">
                  <td class="py-2 pr-4 font-mono text-xs">sidebar-collapsed</td>
                  <td class="py-2 pr-4">
                    Remembers whether the navigation sidebar is collapsed or
                    expanded
                  </td>
                  <td class="py-2 pr-4">Session</td>
                  <td class="py-2">Functional</td>
                </tr>
                <tr>
                  <td class="py-2 pr-4 font-mono text-xs">
                    scrooge_household_context
                  </td>
                  <td class="py-2 pr-4">
                    Stores your currently selected household
                  </td>
                  <td class="py-2 pr-4">Session</td>
                  <td class="py-2">Functional</td>
                </tr>
              </tbody>
            </table>
          </div>
          <p class="mt-3">
            Since all cookies used are either strictly necessary for the
            platform&rsquo;s operation or purely functional (UI preferences),
            they are exempt from the consent requirement under Article 5(3) of
            the ePrivacy Directive (2002/58/EC).
          </p>
        </section>

        <!-- 7. Data Sharing -->
        <section>
          <h2 class="text-xl font-semibold text-pure-white mb-3">
            7. Data Sharing and Third Parties
          </h2>
          <p>
            We do <strong class="text-pure-white">not</strong> sell, rent, or
            share your personal data with third parties for marketing or
            advertising purposes. Your data may be shared only in the following
            circumstances:
          </p>
          <ul class="mt-3 space-y-1 list-disc list-inside">
            <li>
              <strong class="text-pure-white">Household members</strong> &mdash;
              if you join a household, certain data (display name, shared
              financial records) is visible to other household members.
            </li>
            <li>
              <strong class="text-pure-white">Legal obligations</strong> &mdash;
              if required by applicable law, regulation, or valid legal process.
            </li>
            <li>
              <strong class="text-pure-white">Infrastructure providers</strong>
              &mdash; our hosting and database providers process data on our
              behalf under appropriate data processing agreements in compliance
              with GDPR.
            </li>
          </ul>
        </section>

        <!-- 8. Data Retention -->
        <section>
          <h2 class="text-xl font-semibold text-pure-white mb-3">
            8. Data Retention
          </h2>
          <p>
            Your personal data is retained for as long as your account is
            active. If you request account deletion, all personal data and
            associated usage data will be permanently deleted within 30 days of
            your request, unless retention is required by law.
          </p>
        </section>

        <!-- 9. Your Rights -->
        <section>
          <h2 class="text-xl font-semibold text-pure-white mb-3">
            9. Your Rights Under GDPR
          </h2>
          <p>
            As a data subject under the General Data Protection Regulation (EU)
            2016/679, you have the following rights:
          </p>
          <ul class="mt-3 space-y-2 list-disc list-inside">
            <li>
              <strong class="text-pure-white">Right of access (Art. 15)</strong>
              &mdash; you may request confirmation of whether your personal data
              is being processed and obtain a copy of it.
            </li>
            <li>
              <strong class="text-pure-white"
                >Right to rectification (Art. 16)</strong
              >
              &mdash; you may request correction of inaccurate personal data.
              Note: since your email is stored in hashed form, it cannot be
              &ldquo;corrected&rdquo;; instead, you would need to re-register
              with the correct email.
            </li>
            <li>
              <strong class="text-pure-white"
                >Right to erasure (Art. 17)</strong
              >
              &mdash; you may request deletion of your personal data
              (&ldquo;right to be forgotten&rdquo;).
            </li>
            <li>
              <strong class="text-pure-white"
                >Right to restriction of processing (Art. 18)</strong
              >
              &mdash; you may request that we limit the processing of your data
              under certain conditions.
            </li>
            <li>
              <strong class="text-pure-white"
                >Right to data portability (Art. 20)</strong
              >
              &mdash; you may request your data in a structured,
              commonly-used, and machine-readable format.
            </li>
            <li>
              <strong class="text-pure-white">Right to object (Art. 21)</strong>
              &mdash; you may object to processing based on legitimate interest.
            </li>
            <li>
              <strong class="text-pure-white"
                >Right to lodge a complaint</strong
              >
              &mdash; you have the right to file a complaint with a supervisory
              authority. In Poland, the competent authority is the President of
              the Personal Data Protection Office (Prezes Urzedu Ochrony Danych
              Osobowych, UODO), ul. Stawki 2, 00-193 Warsaw, Poland.
            </li>
          </ul>
          <p class="mt-3">
            To exercise any of these rights, please contact the Data Controller
            using the details provided in Section 1.
          </p>
        </section>

        <!-- 10. Security -->
        <section>
          <h2 class="text-xl font-semibold text-pure-white mb-3">
            10. Security Measures
          </h2>
          <p>We implement appropriate technical and organizational measures to protect your personal data, including:</p>
          <ul class="mt-3 space-y-1 list-disc list-inside">
            <li>
              Irreversible hashing of email addresses (SHA-256) &mdash; your
              email cannot be recovered or misused even in the event of a data
              breach.
            </li>
            <li>
              Secure password hashing using the bcrypt algorithm with salt.
            </li>
            <li>
              JWT-based authentication with short-lived access tokens (30
              minutes).
            </li>
            <li>
              Optional two-factor authentication (TOTP) for additional account
              security.
            </li>
            <li>Encrypted data transmission via HTTPS/TLS.</li>
          </ul>
        </section>

        <!-- 11. Changes -->
        <section>
          <h2 class="text-xl font-semibold text-pure-white mb-3">
            11. Changes to This Policy
          </h2>
          <p>
            We reserve the right to update this privacy policy at any time. As
            the platform is in alpha release, changes may occur more frequently
            as features evolve. Material changes will be communicated to
            registered users through the platform&rsquo;s notification system.
            The &ldquo;last updated&rdquo; date at the top of this page reflects
            the most recent revision.
          </p>
        </section>

        <!-- 12. Applicable Law -->
        <section>
          <h2 class="text-xl font-semibold text-pure-white mb-3">
            12. Applicable Law
          </h2>
          <p>
            This privacy policy is governed by the laws of the Republic of
            Poland and the European Union, including the General Data Protection
            Regulation (EU) 2016/679 (GDPR) and the Polish Act on the
            Protection of Personal Data of 10 May 2018.
          </p>
        </section>
      </div>
    </div>

    <LandingFooter />
  </div>
</template>
