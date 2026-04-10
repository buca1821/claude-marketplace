# App Store Rejection Prevention & Handling

## Pre-Submission Audit Checklist

### Guideline 2.x — Performance

- [ ] App does not crash on any supported device/OS
- [ ] No placeholder content (lorem ipsum, TODO, test data in screenshots)
- [ ] App loads within reasonable time (< 10s to first meaningful content)
- [ ] All links work (privacy policy, support URL, marketing URL)
- [ ] Screenshots accurately represent current app UI
- [ ] App description matches actual functionality
- [ ] Beta/test features are not visible to users

### Guideline 3.x — Business

- [ ] No links to external payment methods for digital goods
- [ ] In-app purchases use StoreKit (if applicable)
- [ ] Subscription terms clearly disclosed before purchase
- [ ] Restore purchases button accessible

### Guideline 4.x — Design

- [ ] App provides meaningful value beyond a simple website
- [ ] UI follows Human Interface Guidelines
- [ ] No misleading or copycat design
- [ ] App works without login when possible

### Guideline 5.x — Legal & Privacy

- [ ] Privacy policy URL is valid and accessible
- [ ] Privacy Nutrition Label is accurate and complete
- [ ] Usage descriptions explain WHY data is needed (HealthKit, Location, etc.)
- [ ] App only accesses data it needs (principle of least privilege)
- [ ] Data collection disclosed for all third-party SDKs
- [ ] GDPR compliance for EU users (if applicable)

### Data Access Permissions (adapt to your app's needs)

- [ ] Usage descriptions clearly explain purpose (e.g., `NSHealthShareUsageDescription`, `NSLocationWhenInUseUsageDescription`)
- [ ] App functions if user denies permissions (graceful degradation)
- [ ] User data is NOT shared with third parties without explicit consent
- [ ] Review notes explain how to test data-dependent features
- [ ] If using Background Modes, justified in review notes

## Top 10 Common Rejections

### 1. Guideline 2.1 — App Completeness
**Reason**: Crashes, broken features, placeholder content
**Fix**: Test on all supported devices. Remove TODO/placeholder text. Test with real data.

### 2. Guideline 2.3.3 — Accurate Screenshots
**Reason**: Screenshots don't match current UI
**Fix**: Retake screenshots after every major UI change. Use automation (fastlane snapshot).

### 3. Guideline 4.0 — Design (Minimum Functionality)
**Reason**: App is too simple or replicates built-in functionality
**Fix**: Highlight unique features in review notes. Ensure app provides clear value.

### 4. Guideline 5.1.1 — Data Collection and Storage
**Reason**: Accessing data not justified, missing privacy policy
**Fix**: Only request necessary permissions. Justify each in review notes. Keep privacy policy current.

### 5. Guideline 5.1.2 — Data Use and Sharing
**Reason**: Sharing data with third parties without disclosure
**Fix**: Disclose all third-party SDKs in Privacy Nutrition Label. Get user consent for sharing.

### 6. Guideline 2.3.7 — Accurate Descriptions
**Reason**: Description mentions features that don't exist (yet)
**Fix**: Only describe shipped features. Use "Coming soon" sparingly.

### 7. Guideline 4.8 — Login Information
**Reason**: Reviewer can't test app because it requires login
**Fix**: Provide demo account in review notes, or allow app use without login.

### 8. Guideline 2.1 — Performance Bugs
**Reason**: App hangs, high memory usage, or poor performance
**Fix**: Profile with Instruments before submission. Test on oldest supported device.

### 9. Guideline 3.1.1 — In-App Purchase
**Reason**: Digital goods purchased outside StoreKit
**Fix**: All digital content/features must use StoreKit. Physical goods can use external payment.

### 10. Guideline 1.2 — User Generated Content
**Reason**: Missing content moderation for user-shared content
**Fix**: Add reporting mechanism if app allows sharing between users.

## Review Notes Template

```
Thank you for reviewing YourApp.

## How to Test
1. Launch the app — sample data loads automatically
2. Tap any item to see the detail view
3. Exercise core features (export, filter, share, etc.)

## Data Access
[Explain what data the app accesses and why.]
[Example: The app reads workout data from Apple Health to display and export.]
No user data is shared with third parties.
Permission can be denied — the app shows an informative empty state.

## Notes
- No login required
- No in-app purchases
- No user-generated content
```

## Handling a Rejection

### 1. Read the Rejection Carefully
- Identify the specific guideline cited
- Understand what the reviewer flagged

### 2. Fix or Respond

**If the rejection is valid**: Fix the issue, resubmit.

**If the rejection is unclear**: Reply in Resolution Center asking for clarification.

**If you disagree**: Reply professionally with evidence:

```
Thank you for the review.

Regarding Guideline [X.X]:

[Explain why the rejection doesn't apply, with specific evidence]

[Reference Apple documentation or HIG that supports your implementation]

[Offer to make changes if needed, but explain your reasoning]

We're happy to discuss further or make adjustments.
```

### 3. Escalation Path

1. **Resolution Center** — reply to the rejection (first attempt)
2. **Phone call** — request a call via Resolution Center (second attempt)
3. **App Review Board** — formal appeal at `reportaproblem.apple.com` (last resort)
