<script setup lang="ts">
definePageMeta({
  layout: false,
});

useSeoMeta({
  title: "Terms of Service - LockIner",
  description: "LockIner terms of service and conditions of use",
});
</script>

<template>
  <div class="min-h-screen bg-background-black">
    <LandingNav />

    <div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
      <h1 class="text-3xl font-bold text-pure-white mb-2">Terms of Service</h1>
      <p class="text-pure-white/40 text-sm mb-10">
        Last updated: February 17, 2026
      </p>

      <div class="space-y-8 text-pure-white/70 text-sm leading-relaxed">
        <!-- 1. Introduction -->
        <section>
          <h2 class="text-xl font-semibold text-pure-white mb-3">
            1. Introduction
          </h2>
          <p>
            These Terms of Service (&ldquo;Terms&rdquo;) govern your access to
            and use of the LockIner platform (&ldquo;Platform&rdquo;,
            &ldquo;Service&rdquo;), operated by
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
            By creating an account or using the Platform, you agree to be bound
            by these Terms. If you do not agree, you must not use the Service.
          </p>
        </section>

        <!-- 2. Alpha Release -->
        <section
          class="border border-warning-orange/30 bg-warning-orange/5 rounded-lg p-5"
        >
          <h2 class="text-xl font-semibold text-warning-orange mb-3">
            2. Alpha Release
          </h2>
          <p>
            The Platform is currently in
            <strong class="text-warning-orange">alpha release</strong>.
            This means:
          </p>
          <ul class="mt-3 space-y-2 list-disc list-inside">
            <li>
              Registration is available
              <strong class="text-pure-white">exclusively to invited users</strong>
              who possess a valid voucher code.
            </li>
            <li>
              Features, functionality, and data structures are subject to change
              without prior notice as the Platform evolves.
            </li>
            <li>
              The Service is provided on an &ldquo;as is&rdquo; and &ldquo;as
              available&rdquo; basis. Occasional downtime, bugs, and data loss
              may occur during the alpha period.
            </li>
            <li>
              We reserve the right to reset, modify, or delete data during the
              alpha phase if technically necessary for development purposes.
              Users will be notified in advance when possible.
            </li>
          </ul>
        </section>

        <!-- 3. Account Registration -->
        <section>
          <h2 class="text-xl font-semibold text-pure-white mb-3">
            3. Account Registration
          </h2>
          <p>To register for the Platform, you must:</p>
          <ul class="mt-3 space-y-2 list-disc list-inside">
            <li>
              Provide a valid
              <strong class="text-pure-white">voucher code</strong> issued by
              the Platform operator.
            </li>
            <li>
              Provide a
              <strong class="text-pure-white">display name</strong>.
              <span class="text-warning-orange"
                >We strongly recommend using a nickname or first name only,
                rather than your full legal name</span
              >, as the display name may be visible to other users within shared
              households.
            </li>
            <li>
              Provide a valid
              <strong class="text-pure-white">email address</strong>. Your email
              is immediately and irreversibly hashed (SHA-256) upon registration.
              The Platform does not store your email in readable form and cannot
              use it to contact you, send newsletters, or for any other purpose.
              Your email is used solely for identity verification when you
              manually enter it during login.
            </li>
            <li>
              Create a <strong class="text-pure-white">password</strong> of at
              least 8 characters. Passwords are stored using bcrypt hashing and
              are never kept in plaintext.
            </li>
          </ul>
          <p class="mt-3">
            You are responsible for maintaining the confidentiality of your
            account credentials and for all activities that occur under your
            account. Since the Platform cannot recover or access your email
            address, password recovery via email is not available. You are
            strongly encouraged to enable two-factor authentication (TOTP) for
            additional security.
          </p>
        </section>

        <!-- 4. Description of Service -->
        <section>
          <h2 class="text-xl font-semibold text-pure-white mb-3">
            4. Description of Service
          </h2>
          <p>
            LockIner is a personal productivity and life management platform
            that provides the following modules:
          </p>
          <ul class="mt-3 space-y-1 list-disc list-inside">
            <li>
              <strong class="text-pure-white">Finance</strong> &mdash;
              transaction tracking, receipt management, budgets, and spending
              analytics.
            </li>
            <li>
              <strong class="text-pure-white">Fitness</strong> &mdash; workout
              logging, exercise tracking, weight measurements, and progress
              reports.
            </li>
            <li>
              <strong class="text-pure-white">Food</strong> &mdash; recipe
              management, meal planning, and food data imports.
            </li>
            <li>
              <strong class="text-pure-white">Skills</strong> &mdash; learning
              journeys, progress tracking, and learning logs.
            </li>
            <li>
              <strong class="text-pure-white">Journal</strong> &mdash; daily
              journal entries, history, and reports.
            </li>
            <li>
              <strong class="text-pure-white">Households</strong> &mdash; shared
              financial management, multi-user access, and household invitations.
            </li>
          </ul>
          <p class="mt-3">
            The availability and scope of modules may change during the alpha
            period.
          </p>
        </section>

        <!-- 5. Acceptable Use -->
        <section>
          <h2 class="text-xl font-semibold text-pure-white mb-3">
            5. Acceptable Use
          </h2>
          <p>You agree not to:</p>
          <ul class="mt-3 space-y-2 list-disc list-inside">
            <li>
              Use the Platform for any unlawful purpose or in violation of any
              applicable local, national, or international law.
            </li>
            <li>
              Attempt to gain unauthorized access to the Platform, other users'
              accounts, or any systems or networks connected to the Service.
            </li>
            <li>
              Share, transfer, or sell your voucher code or account credentials
              to third parties.
            </li>
            <li>
              Interfere with or disrupt the integrity or performance of the
              Platform.
            </li>
            <li>
              Upload or transmit malicious code, viruses, or any harmful
              content.
            </li>
            <li>
              Use automated scripts, bots, or scrapers to access the Platform
              without prior written consent.
            </li>
          </ul>
          <p class="mt-3">
            Violation of these terms may result in immediate account suspension
            or termination.
          </p>
        </section>

        <!-- 6. Intellectual Property -->
        <section>
          <h2 class="text-xl font-semibold text-pure-white mb-3">
            6. Intellectual Property
          </h2>
          <p>
            All rights, title, and interest in the Platform &mdash; including
            its source code, design, graphics, logos, and content &mdash; are
            owned by MAKE IT REMOTE Adam Naworski or its licensors. You are
            granted a limited, non-exclusive, non-transferable, revocable
            license to use the Platform in accordance with these Terms.
          </p>
          <p class="mt-3">
            You retain ownership of all data and content you create within the
            Platform. By using the Service, you grant us a limited license to
            store and process your content solely for the purpose of providing
            the Service.
          </p>
        </section>

        <!-- 7. Household and Shared Data -->
        <section>
          <h2 class="text-xl font-semibold text-pure-white mb-3">
            7. Households and Shared Data
          </h2>
          <p>
            The Platform allows you to create or join households for shared
            financial management. When participating in a household:
          </p>
          <ul class="mt-3 space-y-2 list-disc list-inside">
            <li>
              Your display name and shared financial data will be visible to
              other household members.
            </li>
            <li>
              You are responsible for the data you share within a household.
            </li>
            <li>
              Household creators may manage membership and invitation settings.
            </li>
          </ul>
        </section>

        <!-- 8. Limitation of Liability -->
        <section>
          <h2 class="text-xl font-semibold text-pure-white mb-3">
            8. Limitation of Liability
          </h2>
          <p>
            To the maximum extent permitted by applicable law, MAKE IT REMOTE
            Adam Naworski shall not be liable for any indirect, incidental,
            special, consequential, or punitive damages, including but not
            limited to loss of data, profits, or business opportunities,
            arising from your use of or inability to use the Platform.
          </p>
          <p class="mt-3">
            Given the alpha nature of the Platform, we do not guarantee
            uninterrupted availability, data integrity, or the continued
            existence of any specific feature. You acknowledge and accept these
            risks by using the Service.
          </p>
          <p class="mt-3">
            Nothing in these Terms excludes or limits liability for death,
            personal injury caused by negligence, fraud, or any other liability
            that cannot be excluded under applicable EU or Polish law.
          </p>
        </section>

        <!-- 9. Account Termination -->
        <section>
          <h2 class="text-xl font-semibold text-pure-white mb-3">
            9. Account Termination
          </h2>
          <p>
            You may request deletion of your account at any time by contacting
            the Platform operator. Upon deletion, all your personal data and
            associated content will be permanently removed within 30 days.
          </p>
          <p class="mt-3">
            We reserve the right to suspend or terminate your account at any
            time if you violate these Terms, or if necessary for technical,
            legal, or security reasons. We will make reasonable efforts to
            notify you prior to termination when circumstances permit.
          </p>
        </section>

        <!-- 10. Disclaimers -->
        <section>
          <h2 class="text-xl font-semibold text-pure-white mb-3">
            10. Disclaimers
          </h2>
          <ul class="space-y-2 list-disc list-inside">
            <li>
              The Platform is not a financial advisor, medical professional, or
              dietary consultant. Any data provided through the Finance,
              Fitness, and Food modules is for personal tracking purposes only
              and should not be relied upon as professional advice.
            </li>
            <li>
              The Platform does not store your email in readable form. As a
              result, we cannot send you email notifications, password reset
              links, or any email communications. You are solely responsible
              for remembering your credentials.
            </li>
          </ul>
        </section>

        <!-- 11. Changes to Terms -->
        <section>
          <h2 class="text-xl font-semibold text-pure-white mb-3">
            11. Changes to These Terms
          </h2>
          <p>
            We reserve the right to modify these Terms at any time. During the
            alpha period, changes may occur more frequently as the Platform
            evolves. Material changes will be communicated through the
            Platform&rsquo;s notification system. Your continued use of the
            Service after changes are posted constitutes acceptance of the
            revised Terms.
          </p>
        </section>

        <!-- 12. Governing Law -->
        <section>
          <h2 class="text-xl font-semibold text-pure-white mb-3">
            12. Governing Law and Dispute Resolution
          </h2>
          <p>
            These Terms are governed by the laws of the Republic of Poland and
            the applicable regulations of the European Union. Any disputes
            arising from or relating to these Terms or your use of the Platform
            shall be subject to the exclusive jurisdiction of the courts
            competent for the registered address of the operator (Olawa,
            Poland).
          </p>
          <p class="mt-3">
            If you are a consumer residing in the European Union, you retain
            any mandatory consumer protection rights granted by the laws of
            your country of residence that cannot be waived by contract. You
            may also use the EU Online Dispute Resolution platform at
            <a
              href="https://ec.europa.eu/consumers/odr"
              target="_blank"
              rel="noopener noreferrer"
              class="text-cyber-blue hover:underline"
              >https://ec.europa.eu/consumers/odr</a
            >.
          </p>
        </section>

        <!-- 13. Contact -->
        <section>
          <h2 class="text-xl font-semibold text-pure-white mb-3">
            13. Contact
          </h2>
          <p>
            For any questions regarding these Terms of Service, please contact
            MAKE IT REMOTE Adam Naworski using the contact details available
            through the official CEIDG registry entry or through the
            Platform&rsquo;s contact channels.
          </p>
        </section>
      </div>
    </div>

    <LandingFooter />
  </div>
</template>
