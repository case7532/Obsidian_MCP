# Circular 64/2024/TT-NHNN — Open API in Banking Sector

**Source**: Circular No. 64/2024/TT-NHNN dated December 31, 2024 of the Governor of the State Bank of Vietnam
**Effective**: March 01, 2025
**Compliance Deadline**: March 01, 2027 (for banks already operating APIs before effective date)

This extension enforces compliance with SBV Circular 64 on implementation of Open Application Programming Interface in the banking sector. Rules are derived from the Circular's main body, Appendix 01 (API specifications), and Appendix 02 (Technical standards).

---

## Rule C64-01: REST Architecture and JSON Format

**Rule**: All Open APIs MUST use REpresentational State Transfer (REST) architecture and JavaScript Object Notation (JSON) as the data interchange format. SOAP and XML are only recommended for other (non-Open) bank APIs.

**Reference**: Appendix 02, Section 1 (Architectural standards)

**Verification**: Check that all API endpoints use REST conventions (HTTP methods, resource-based URLs) and accept/return JSON (Content-Type: application/json).

---

## Rule C64-02: OAuth 2.0 Authentication and Authorization

**Rule**: All Open APIs MUST implement OAuth 2.0 authorization framework compliant with RFC 6749, RFC 6750, and RFC 7636 (PKCE). OpenID Connect (OIDC) MAY be combined with OAuth 2.0 depending on use cases. Specifically:
- Payment Initiation (PIS) APIs use Authorization Code Grant (RFC 6749 Section 4.1) via Redirect Flow, or Client Credentials Grant (RFC 6749 Section 4.4) via Decoupled Flow.
- E-wallet cash-in/cash-out (EWLTS) APIs use Client Credentials Grant (RFC 6749 Section 4.4).
- Token revocation MUST follow RFC 7009.

**Reference**: Appendix 02, Section 3.1; Appendix 01, Sections 4-6

**Verification**: Check that OAuth 2.0 flows are correctly implemented with PKCE support, proper grant types per API group, and token lifecycle management (issuance, refresh, revocation).

---

## Rule C64-03: Transport Layer Security

**Rule**: All API communications MUST use HTTPS with TLS version 1.2 or higher. Mutual TLS (mTLS) is recommended.

**Reference**: Appendix 02, Section 3.2

**Verification**: Check that all endpoints enforce HTTPS, TLS 1.2+ is configured, and older TLS/SSL versions are disabled.

---

## Rule C64-04: JWS Digital Signature

**Rule**: All API requests and responses MUST include a JWS (JSON Web Signature) in the header (JWS-Signature field), compliant with RFC 7515. Minimum key length: 2048 bits for RSA, 256 bits for ECDSA.

**Reference**: Appendix 02, Section 3.4; Appendix 01, all API specifications

**Verification**: Check that every API request/response includes JWS-Signature header, signing keys meet minimum length requirements, and signature verification is implemented on both sides.

---

## Rule C64-05: Encryption Standards

**Rule**: Data encryption SHOULD use one of the following:
- AES (TCVN 7816:2007)
- RSA (PKCS#1 v2.1+, RSAES-OAEP, minimum 2048-bit key)
- ECC (minimum 256-bit key)
- JWE (RFC 7516)

**Reference**: Appendix 02, Section 3.3

**Verification**: Check that sensitive data fields are encrypted using approved algorithms with compliant key lengths.

---

## Rule C64-06: Hash Algorithm for Digital Signature

**Rule**: Digital signatures SHOULD use one of: SHA-256, SHA-384, SHA-512, SHA-512/256, SHA3-256, SHA3-384, SHA3-512, SHAKE128, SHAKE256 (per FIPS PUB 180-4 and FIPS PUB 202).

**Reference**: Appendix 02, Section 3.5

**Verification**: Check that signing algorithms use approved hash functions. SHA-1 and MD5 MUST NOT be used.

---

## Rule C64-07: Data Standards Compliance

**Rule**: APIs MUST comply with the following data standards:
- Currency codes: ISO 4217 (3 uppercase letters)
- Date/time format: RFC 3339 (yyyy-MM-ddTHH:mm:ssZ, UTC)
- Data format: ISO 20022 is recommended for financial messaging

**Reference**: Appendix 02, Section 2

**Verification**: Check that all currency fields use ISO 4217, all datetime fields use RFC 3339 format, and transaction status codes follow ISO 20022.

---

## Rule C64-08: Mandatory API Headers

**Rule**: All Open API requests MUST include the following headers where specified:
- `Content-Type`: application/json (M)
- `Authorization`: Bearer {access_token} per RFC 6750 (M)
- `Request-DateTime`: RFC 3339 UTC format (M)
- `Request-ID`: UUID format, max 60 chars (M)
- `Provider-ID`: Bank identification code, max 8 chars (M)
- `TPP-ID`: Third-party identifier, max 15 chars (M)
- `JWS-Signature`: JWS signature (M)
- `Client-ID`: max 50 chars (O)
- `PSU-IP-Address`: IPv4 or IPv6 (O)
- `PSU-User-Agent`: max 200 chars (O)
- `PSU-Device-OS`: max 100 chars (O)

Response headers MUST include: Content-Type, Request-ID (echoed), Request-DateTime (echoed), JWS-Signature.

**Reference**: Appendix 01, all API specifications

**Verification**: Check that all API controllers validate mandatory headers and echo required headers in responses.

---

## Rule C64-09: E-Wallet API Endpoints (EWLTS Scope)

**Rule**: E-wallet Open APIs MUST implement the following endpoints with exact paths and methods. All EWLTS APIs use `client_credentials` grant type only (no Authorization Code Grant, no Redirect, no PKCE). The `ewalletToken` field (generated during wallet-bank linking) is mandatory for ALL e-wallet operations.

### EWLTS Cash-in APIs (Section 5)

Prerequisite: Customer has completed e-wallet linking with the bank (has valid `ewalletToken`).

| # | API | Endpoint | Method | Scope | Direction |
|---|-----|----------|--------|-------|-----------|
| 5.1 | Initialize cash-in | `/v1/cash-in` | POST | EWLTS | TPP → Bank |
| 5.2 | Verify OTP | `/v1/verify-otp-cash-in` | POST | EWLTS | TPP → Bank |
| 5.3 | Update consent (Decoupled) | `/v1/update-consent-cash-in` | POST | — | **Bank → TPP** |
| 5.4 | Get consent (Decoupled) | `/v1/get-consent-cash-in` | POST | EWLTS | TPP → Bank |
| 5.5 | Confirm cash-in | `/v1/submit-cash-in` | POST | EWLTS | TPP → Bank |
| 5.6 | Get transaction status | `/v1/get-status-cash-in` | POST | EWLTS | TPP → Bank |

### EWLTS Cash-out API (Section 6)

| # | API | Endpoint | Method | Scope | Direction |
|---|-----|----------|--------|-------|-----------|
| 6 | Cash-out | `/v1/cash-out` | POST | EWLTS | TPP → Bank |

### Key Difference from PIS (Section 4)

| Aspect | PIS | EWLTS Cash-in |
|--------|-----|---------------|
| OAuth grant type | client_credentials + authorization_code (Redirect) | **client_credentials only** |
| Customer auth | Redirect Flow or Decoupled Flow | **OTP Flow** or Decoupled Flow or NONE |
| Redirect Flow | Yes (GET /authorize → POST /token) | **No** — replaced by OTP |
| Distinctive required field | creditor/debtor | **ewalletToken** (all APIs) |
| Init response | consentStatus = AWAITTING_AUTH | **authType** (OTP / DECOUPLED / NONE) |
| OTP verification API | None | **POST /v1/verify-otp-cash-in** |

### EWLTS Cash-in Flow — OTP Flow

```
PSU (Customer)          TPP Application           Bank Auth Server         Bank Open API
      |                       |                         |                       |
      |---(1) Cash-in req---->|                         |                       |
      |                       |---(2) client_credentials grant----------------->|
      |                       |<--(2.1) access_token--------------------------------|
      |                       |---(3) POST /v1/cash-in [ewalletToken]---------->|
      |                       |<--(3.1) paymentId, authType="OTP"---------------|
      |                       |                         |                       |
      |<-------(4) Bank sends OTP to customer (SMS/push)------------------------|
      |---(4.1) Enter OTP---->|                         |                       |
      |                       |---(4.2) POST /v1/verify-otp-cash-in------------>|
      |                       |   {paymentId, OTP, ewalletToken}                |
      |                       |<--(4.2.2) consentId, expireIn--------------------|
      |                       |                         |                       |
      |                       |---(5) POST /v1/submit-cash-in [consentId]------>|
      |                       |<--(5.1) paymentId, status, statusDateTime-------|
      |                       |                         |                       |
      |                       |---(6) POST /v1/get-status-cash-in [if needed]-->|
      |                       |<--(6.1) paymentId, status, statusDateTime-------|
      |<--(7) Display result--|                         |                       |
```

### EWLTS Cash-in Flow — Decoupled Flow

```
PSU (Customer)          TPP Application           Bank Auth Server         Bank Open API
      |                       |                         |                       |
      |---(1) Cash-in req---->|                         |                       |
      |                       |---(2) client_credentials grant----------------->|
      |                       |<--(2.1) access_token--------------------------------|
      |                       |---(3) POST /v1/cash-in [ewalletToken]---------->|
      |                       |<--(3.1) paymentId, authType="DECOUPLED"---------|
      |                       |                         |                       |
      |<--(4') Notification (optional)------------------|                       |
      |---(4.1') Open banking app----->|                |                       |
      |      (4.1.1') Confirm cash-in info              |                       |
      |      (4.1.2') Authorize per bank auth method    |                       |
      |                       |<--(4.2') POST /v1/update-consent-cash-in--------|
      |                       |   {paymentId, consentId, consentStatus, ewalletToken, expireIn}
      |                       |---(4.2.1') Response: {message: "Success"}------>|
      |                       |                         |                       |
      |                       |---(4.3') POST /v1/get-consent-cash-in [fallback]>|
      |                       |<--(4.3.1') {paymentId, consentId, consentStatus}|
      |                       |                         |                       |
      |                       |---(5) POST /v1/submit-cash-in [consentId]------>|
      |                       |<--(5.1) paymentId, status, statusDateTime-------|
      |                       |                         |                       |
      |                       |---(6) POST /v1/get-status-cash-in [if needed]-->|
      |                       |<--(6.1) paymentId, status, statusDateTime-------|
      |<--(7) Display result--|                         |                       |
```

### EWLTS Cash-in Flow — NONE (No additional auth)

When `authType = "NONE"`, skip authentication steps entirely — proceed directly from step 3.1 to step 5 (submit).

### EWLTS Auth Flow State Machine

```
                POST /v1/cash-in
                      |
                      v
              authType returned
              /       |       \
             /        |        \
          "OTP"  "DECOUPLED"  "NONE"
            |         |          |
            v         v          |
     Bank sends   KH consent    |
     OTP to KH    on bank app   |
            |         |          |
            v         v          |
     verify-otp  update-consent  |
     → consentId → consentId     |
            \         |         /
             \        |        /
              v       v       v
          POST /v1/submit-cash-in
                      |
                      v
            Transaction status (ISO 20022)
```

### EWLTS Token Constraints

| Token/Value | Lifetime | Notes |
|---|---|---|
| access_token (client_credentials) | Max 3600s | Used for all EWLTS APIs |
| consentId (from OTP verify) | 300s | Returned after successful OTP verification |
| consentId (from Decoupled) | 300s | Returned after customer consent on banking app |

### EWLTS Cash-in API Request/Response Summary

**5.1 POST /v1/cash-in** — Initialize cash-in:
- Request body: `instructionIdentification` (String[50], M), `remittanceInformation` (String[255], M), `InstructAmount` {value, currency} (Object, M), `requestedExecutionDate` (DateTime, M), `ewalletToken` (String[30], M), `additionalInfo` (Object, O)
- Response body: `paymentId` (String[35], M), `status` (String[4], M — ISO 20022), `statusDateTime` (DateTime, M), **`authType`** (String[10], M — `"OTP"` / `"DECOUPLED"` / `"NONE"`), `additionalInfo` (Object, O)
- Note: No creditor/debtor fields — `ewalletToken` identifies the linked account

**5.2 POST /v1/verify-otp-cash-in** — OTP Verification:
- Request body: `paymentId` (String[35], M), `OTP` (String[6], M), `ewalletToken` (String[30], M), `additionalInfo` (Object, O)
- Response body: `paymentId` (String[35], M), `consentId` (String[36], M), `expireIn` (Number, M)

**5.3 POST /v1/update-consent-cash-in** — Update consent (Bank → TPP):
- Direction: **Bank calls TPP** (TPP must expose this endpoint)
- Simplified headers: only `Content-Type`, `Authorization`, `Request-DateTime`, `Request-ID`, `Provider-ID`, `JWS-Signature` (no PSU-*, TPP-ID, Client-ID — Bank is the caller)
- Request body: `paymentId` (String[35], M), `consentId` (String[36], M), `consentStatus` (String[20], M), `ewalletToken` (String[30], M), `expireIn` (Number, M)
- Response body: `message` (String[20], M — default `"Success"`)
- Error codes: According to TPP regulations (not Bank's error table)

**5.4 POST /v1/get-consent-cash-in** — Get consent (TPP → Bank):
- Request body: `paymentId` (String[35], M), `ewalletToken` (String[30], M)
- Response body: `paymentId` (String[35], M), `consentId` (String[36], M), `consentStatus` (String[20], M), `expireIn` (Number, M), `ewalletToken` (String[30], M)

**5.5 POST /v1/submit-cash-in** — Confirm cash-in:
- Request body: `paymentId` (String[35], M), `consentId` (String[36], C — required for OTP and Decoupled, not needed for NONE), `ewalletToken` (String[30], M)
- Response body: `paymentId` (String[35], M), `status` (String[4], M — ISO 20022), `statusDateTime` (DateTime, M)

**5.6 POST /v1/get-status-cash-in** — Get transaction status:
- Request body: `paymentId` (String[35], M), `ewalletToken` (String[30], M)
- Response body: `paymentId` (String[35], M), `status` (String[4], M — ISO 20022), `statusDateTime` (DateTime, M)

### EWLTS Cash-out API Summary (Section 6)

**POST /v1/cash-out** — E-wallet cash-out:
- Simple flow: no customer authentication required (steps 1 → 2 → 3 → 3.1 → 3.2 only)
- Request body: `instructionIdentification` (String[50], M), `remittanceInformation` (String[255], M), `InstructAmount` {value, currency} (Object, M), `requestedExecutionDate` (DateTime, M), `ewalletToken` (String[30], M), `additionalInfo` (Object, O)
- Response body: `status` (String[4], M — ISO 20022), `statusDateTime` (DateTime, M)
- Note: No `paymentId` in response (simpler than cash-in), no consent flow

### EWLTS Mandatory Headers

All EWLTS API requests (TPP → Bank) MUST include: `Content-Type`, `Authorization`, `Request-DateTime`, `Request-ID`, `Provider-ID`, `TPP-ID`, `JWS-Signature`. Optional: `PSU-IP-Address`, `PSU-User-Agent`, `PSU-Device-OS`, `Client-ID`.

Bank → TPP callback (`/v1/update-consent-cash-in`) uses simplified headers: `Content-Type`, `Authorization`, `Request-DateTime`, `Request-ID`, `Provider-ID`, `JWS-Signature` only.

All EWLTS API responses MUST echo: `Content-Type`, `Request-ID`, `Request-DateTime`, `JWS-Signature`.

**Reference**: Appendix 01, Sections 5-6

**Verification**:
- Check that all 7 EWLTS endpoints exist with correct paths and HTTP methods
- Check that ALL APIs include `ewalletToken` in request body
- Check that `/v1/cash-in` response includes `authType` field with values OTP/DECOUPLED/NONE
- Check that OTP flow implements `/v1/verify-otp-cash-in` with 6-digit OTP field
- Check that Decoupled flow exposes `/v1/update-consent-cash-in` for Bank callbacks with simplified headers
- Check that `/v1/submit-cash-in` accepts `consentId` as conditional (required for OTP and Decoupled, not for NONE)
- Check that `/v1/cash-out` is a simple flow with no consent/auth steps
- Check that consent status values are: "AUTHORISED", "REJECTED", "CANCEL"
- Check that consentId has max 300s lifetime
- Check that all EWLTS APIs use only `client_credentials` grant type (no authorization_code)

---

## Rule C64-10: Payment Initiation API Endpoints (PIS Scope)

**Rule**: Payment initiation Open APIs MUST implement the following endpoints:

| # | API | Endpoint | Method | Scope | OAuth Grant Type |
|---|-----|----------|--------|-------|-----------------|
| 4.1 | Payment initiation | `/v1/payments` | POST | PIS | client_credentials |
| 4.2 | Customer authorization (Redirect) | `/authorize` | GET | — | Authorization Code + PKCE |
| 4.3 | Get access token (Redirect) | `/token` | POST | — | authorization_code |
| 4.4 | Update payment consent (Decoupled, Bank→TPP) | `/v1/update-consent` | POST | — | client_credentials |
| 4.5 | Confirm payment | `/v1/payments/submit` | POST | PIS | authorization_code (Redirect) / client_credentials (Decoupled) |
| 4.6 | Get transaction status | `/v1/payments/status` | POST | PIS | client_credentials |
| 4.7 | Get payment consent (Decoupled, TPP→Bank) | `/v1/get-consent` | POST | PIS | client_credentials |

### PIS Flow — Redirect Flow

```
PSU (Customer)          TPP Application           Bank Auth Server         Bank Open API
      |                       |                         |                       |
      |---(1) Payment req---->|                         |                       |
      |                       |---(2) client_credentials grant----------------->|
      |                       |<--(2.1) access_token--------------------------------|
      |                       |---(3) POST /v1/payments [access_token]--------->|
      |                       |<--(3.1) paymentId, consentStatus=AWAITTING_AUTH-|
      |                       |                         |                       |
      |<--(4) Redirect to Bank auth page--------------->|                       |
      |---(4.1) Login + confirm payment---------------->|                       |
      |      (4.1.1) Confirm payment info               |                       |
      |      (4.1.2) Authorize per bank auth method     |                       |
      |<--(4.1.3) Redirect back with authorization code-|                       |
      |                       |---(4.2) POST /token [code + code_verifier]----->|
      |                       |<--(4.2.2) access_token (single-use, PIS)--------|
      |                       |---(5) POST /v1/payments/submit [access_token]-->|
      |                       |<--(5.1) paymentId, status, statusDateTime-------|
      |                       |                         |                       |
      |                       |---(6) POST /v1/payments/status [if no response]>|
      |                       |<--(6.1) paymentId, status, statusDateTime-------|
      |<--(7) Display result--|                         |                       |
```

Redirect Flow specifics:
- `/authorize` uses `response_type = "code id_token"` (differs from AIS which uses `"code"`)
- `/authorize` scope: `PIS`
- PKCE required: `code_challenge = BASE64URL-ENCODE(SHA256(ASCII(code_verifier)))`, method `S256`
- `/authorize` `request` parameter: JWT containing `paymentId` in payload claim
- `/token` uses `grant_type = authorization_code` with `code_verifier` for PKCE verification
- Resulting `access_token` is **single-use**, max validity **300 seconds**

### PIS Flow — Decoupled Flow

```
PSU (Customer)          TPP Application           Bank Auth Server         Bank Open API
      |                       |                         |                       |
      |---(1) Payment req---->|                         |                       |
      |                       |---(2) client_credentials grant----------------->|
      |                       |<--(2.1) access_token--------------------------------|
      |                       |---(3) POST /v1/payments [access_token]--------->|
      |                       |<--(3.1) paymentId, consentStatus=AWAITTING_AUTH-|
      |                       |                         |                       |
      |<--(4') Notification (optional)------------------|                       |
      |---(4.1') Open banking app----->|                |                       |
      |      (4.1.1') Confirm payment info              |                       |
      |      (4.1.2') Authorize per bank auth method    |                       |
      |                       |<--(4.2') POST /v1/update-consent [Bank→TPP]----|
      |                       |   {paymentId, consentId, consentStatus, expireIn}
      |                       |---(4.2.1') Response: {message: "Success"}------>|
      |                       |                         |                       |
      |                       |---(4.3') POST /v1/get-consent [if no callback]>|
      |                       |<--(4.3.1') {paymentId, consentId, consentStatus}|
      |                       |                         |                       |
      |                       |---(5') POST /v1/payments/submit [+ consentId]-->|
      |                       |<--(5.1') paymentId, status, statusDateTime------|
      |                       |                         |                       |
      |                       |---(6) POST /v1/payments/status [if no response]>|
      |                       |<--(6.1) paymentId, status, statusDateTime-------|
      |<--(7) Display result--|                         |                       |
```

Decoupled Flow specifics:
- All Bank→TPP and TPP→Bank calls use `grant_type = client_credentials`
- Bank calls TPP's `/v1/update-consent` endpoint (Bank is the caller, TPP is the server)
- TPP can poll via `/v1/get-consent` as fallback if callback not received
- `consentId` is generated by Bank after successful customer consent on banking app

### PIS Token Constraints

| Token/Value | Lifetime | Usage | Notes |
|---|---|---|---|
| access_token (client_credentials) | Max 3600s | Multiple use | For payment initiation (step 2) and status queries |
| Authorization Code | 180s | **Single use** | From `/authorize` redirect |
| access_token (authorization_code, PIS) | Max 300s | **Single use** | For payment submit only (Redirect Flow) |
| consentId | 300s | Single use | Generated after customer consent (Decoupled Flow) |
| consentStatus initial | — | — | Default: `"AWAITTING_AUTH"` |

### PIS Consent State Machine

```
                    POST /v1/payments
                          |
                          v
                  [AWAITTING_AUTH]
                   /      |      \
                  /       |       \
    Customer     /   Customer  Customer
    approves    /    fails     cancels
              v        v          v
        [AUTHORISED] [REJECTED] [CANCEL]
              |
              v
        POST /v1/payments/submit
              |
              v
        Transaction status (ISO 20022)
```

Consent status values: `"AUTHORISED"`, `"REJECTED"`, `"CANCEL"`

### PIS API Request/Response Summary

**4.1 POST /v1/payments** — Payment Initiation:
- Request body: `instructionIdentification` (String[50], M), `creditor` {name, accountId, bankCode} (Object, M), `debtor` {name, accountId, bankCode} (Object, C — not required for Payment Gateway), `remittanceInformation` (String[255], M), `InstructAmount` {value, currency} (Object, M), `requestedExecutionDate` (DateTime, M), `additionalInfo` (Object, O)
- Response body: `paymentId` (String[35], M), `status` (String[4], M — ISO 20022), `statusDateTime` (DateTime, M), `consentStatus` (String[20], M — default `"AWAITTING_AUTH"`)

**4.2 GET /authorize** — Customer Authorization (Redirect):
- Query params: `response_type` = `"code id_token"`, `client_id`, `scope` = `"PIS"`, `redirect_uri`, `state`, `code_challenge`, `code_challenge_method` = `"S256"` (O), `request` (JWT with paymentId in payload)
- Response (via redirect_uri): `code`, `state`, `id_token` (O, JWT with paymentId)

**4.3 POST /token** — Get Access Token (Redirect):
- Request body: `grant_type` = `"authorization_code"`, `code`, `redirect_uri`, `code_verifier`
- Response body: `access_token`, `token_type` = `"Bearer"`, `expires_in`, `scope`

**4.4 POST /v1/update-consent** — Update Consent (Decoupled, Bank→TPP):
- Direction: **Bank calls TPP** (TPP must expose this endpoint)
- Authorization: Bearer token via client_credentials (RFC 6749 section 4.4)
- Request body: `paymentId` (String[35], M), `consentId` (String[36], M), `consentStatus` (String[20], M), `expireIn` (Number, M)
- Response body: `message` (String[20], M — default `"Success"`)

**4.5 POST /v1/payments/submit** — Confirm Payment:
- Authorization: Bearer token — authorization_code grant (Redirect) or client_credentials (Decoupled)
- Request body: `paymentId` (String[35], M), `consentId` (String[36], C — required for Decoupled)
- Response body: `paymentId` (String[35], M), `status` (String[4], M — ISO 20022), `statusDateTime` (DateTime, M)

**4.6 POST /v1/payments/status** — Get Transaction Status:
- Authorization: Bearer token via client_credentials
- Request body: `paymentId` (String[35], M)
- Response body: `paymentId` (String[35], M), `status` (String[4], M — ISO 20022), `statusDateTime` (DateTime, M)

**4.7 POST /v1/get-consent** — Get Consent Status (Decoupled, TPP→Bank):
- Authorization: Bearer token via client_credentials
- Request body: `paymentId` (String[35], M)
- Response body: `paymentId` (String[35], M), `consentId` (String[36], M), `consentStatus` (String[20], M), `expireIn` (Number, M)

### PIS Mandatory Headers

All PIS API requests MUST include: `Content-Type`, `Authorization`, `Request-DateTime`, `Request-ID`, `Provider-ID`, `TPP-ID`, `JWS-Signature`. Optional: `PSU-IP-Address`, `PSU-User-Agent`, `PSU-Device-OS`, `Client-ID`.

All PIS API responses MUST echo: `Content-Type`, `Request-ID`, `Request-DateTime`, `JWS-Signature`.

**Reference**: Appendix 01, Section 4

**Verification**:
- Check that all 7 PIS endpoints exist with correct paths and HTTP methods
- Check that Redirect Flow implements Authorization Code Grant with PKCE (code_challenge S256)
- Check that Decoupled Flow implements client_credentials grant and exposes `/v1/update-consent` for Bank callbacks
- Check that access_token for PIS authorization_code grant is single-use with max 300s lifetime
- Check that consentId has max 300s lifetime
- Check that `/authorize` uses `response_type = "code id_token"` and includes JWT `request` parameter with paymentId
- Check that `/v1/payments/submit` accepts both Redirect (authorization_code token) and Decoupled (client_credentials token + consentId) flows
- Check that consent state transitions follow: AWAITTING_AUTH → AUTHORISED/REJECTED/CANCEL

---

## Rule C64-11: Consent Management

**Rule**: The system MUST implement customer consent management:
- Consent status values: "AUTHORISED", "REJECTED", "CANCEL"
- Default initial consent status: "AWAITTING_AUTH"
- Customer data access time limit: maximum 180 days after consent (unless otherwise agreed)
- Customers MUST be able to search their consented data and withdraw consent
- Both bank and TPP must provide consent search and withdrawal tools

**Reference**: Articles 4, 11(5-6), 12(2a); Appendix 01

**Verification**: Check that consent status enum is correctly implemented, time limits are enforced, and consent management UI/API exists.

---

## Rule C64-12: Audit Logging and Monitoring

**Rule**: The system MUST:
- Record comprehensive logs of all Open API usage by third parties
- Retain detailed logs for at least 3 months
- Store log data for at least 1 year for inspection purposes
- Implement a monitoring system to detect and prevent unauthorized or suspicious access
- Implement rate limiting to restrict automated queries for customer information

**Reference**: Articles 11(9), 11(12)

**Verification**: Check that API logging captures all requests/responses with timestamps, log retention policies are configured (3 months detailed, 1 year storage), anomaly detection is in place, and rate limiting is implemented.

---

## Rule C64-13: Error Response Compliance

**Rule**: Error responses MUST follow the standardized format:
- OAuth errors: `error`, `error_description`, `error_uri` fields per RFC 6749 Section 5.2
- API errors: `code` (string) and `description` (string) fields
- HTTP status codes and error codes MUST match the General Error Code Table defined in Appendix 01 Section 7
- Standard error codes include: ACCOUNT_ID_REQUIRED, EXPIRED_TOKEN, JWS_SIGNATURE_UNVERIFIED, FORBIDDEN, INTERNAL_ERROR, etc.

**Reference**: Appendix 01, Section 7

**Verification**: Check that all error responses use the standardized format, correct HTTP status codes, and error codes from the defined table.

---

## Rule C64-14: Information System Security Level

**Rule**: The bank's information system implementing Open API MUST comply with Level 3 security requirements per government regulations on information system security levels. Must apply either ISO 27001:2022 or TCVN 11930:2017.

**Reference**: Article 11(4); Appendix 02, Section 3.6

**Verification**: Check that security controls align with Level 3 requirements and either ISO 27001:2022 or TCVN 11930:2017 framework is referenced in security design.

---

## Rule C64-15: Third-Party Access Control

**Rule**: The system MUST:
- Validate third-party identity before granting API access
- Support updating or revoking third-party access rights per contract changes
- Restrict Open APIs for payment initiation, e-wallet cash-in, and e-wallet cash-out to banks and licensed payment intermediary service providers only
- Implement contract-based access with defined scope and purpose

**Reference**: Articles 5(3), 8, 10, 11(10-11)

**Verification**: Check that TPP onboarding validates identity, access scopes are contract-based, revocation mechanisms exist, and TPP type restrictions are enforced for PIS/EWLTS APIs.

---

## Rule C64-16: Open API Testing System

**Rule**: Banks MUST provide an Open API testing system (sandbox) for third parties to test APIs before official implementation. Banks MUST disclose on their official website: information about the testing system and the list of Open APIs they implement.

**Reference**: Articles 3(3), 9

**Verification**: Check that a sandbox/testing environment is planned or available, and API documentation is publicly accessible.

---

## Rule C64-17: Account Information Service API Endpoints (AIS Scope)

**Rule**: Account information Open APIs MUST implement the following endpoints. AIS is the ONLY API group that uses `refresh_token` and long-lived consent (max 180 days per Article 11, Clause 6). Only applies to queries that customers actively initiate on the TPP application.

### AIS APIs (Section 3)

| # | API | Endpoint | Method | Scope | Content-Type | Auth Header |
|---|-----|----------|--------|-------|-------------|-------------|
| 3.1 | Confirm & get consent | `/authorize` | GET | — | x-www-form-urlencoded | — (query params) |
| 3.2 | Get access token | `/token` | POST | — | x-www-form-urlencoded | Basic BASE64(client_id:client_secret) |
| 3.3 | Refresh access token | `/token` | POST | — | x-www-form-urlencoded | Basic BASE64(client_id:client_secret) |
| 3.4 | Revoke access token | `/revoke` | POST | — | x-www-form-urlencoded | Basic BASE64(client_id:client_secret) |
| 3.5 | Get list of accounts | `/v1/accounts` | GET | AIS | application/json | Bearer access_token |
| 3.6 | Get account information | `/v1/accounts/information` | POST | AIS | application/json | Bearer access_token |
| 3.7 | Get transaction history | `/v1/accounts/transactions` | POST | AIS | application/json | Bearer access_token |

**Critical distinction**: Auth APIs (3.1–3.4) use `x-www-form-urlencoded` and `Basic` auth. Data APIs (3.5–3.7) use `application/json` and `Bearer` token. Auth APIs do NOT require JWS-Signature header.

### Key Differences from PIS and EWLTS

| Aspect | AIS (Section 3) | PIS (Section 4) | EWLTS (Section 5) |
|--------|-----------------|-----------------|-------------------|
| OAuth grant type | Authorization Code + PKCE | authorization_code (Redirect) / client_credentials (Decoupled) | client_credentials only |
| Has refresh_token | **Yes** — AIS only | No | No |
| Has revoke token | **Yes** — when customer withdraws consent | No | No |
| Consent duration | **Max 180 days** (Article 11, Clause 6) | Single-use (300s) | Single-use (300s) |
| response_type | `"code"` | `"code id_token"` | No /authorize |
| JWT request param in /authorize | **No** | Yes (contains paymentId) | N/A |

### AIS Flow — Part 1: Access Token Retrieval

```
PSU (Customer)          TPP Application           Bank Auth Server
      |                       |                         |
      |---(1) Login + request data sharing consent----->|
      |                       |                         |
  [If no consent or consent expired (>180 days)]        |
      |                       |                         |
      |<--(1.1) Redirect to Bank auth page------------->|
      |---(2) Login on Bank auth page------------------>|
      |      (2.1) Bank authenticates + KH confirms     |
      |           data sharing consent                  |
      |<--(2.2) Redirect back: redirect_uri?code&state--|
      |                       |---(2.3) POST /token---->|
      |                       |   {grant_type=authorization_code,
      |                       |    code, redirect_uri, code_verifier}
      |                       |<--(2.3.1) access_token + refresh_token
      |                       |                         |
  [If consent valid but access_token expired]           |
      |                       |                         |
      |                       |---(3) POST /token------>|
      |                       |   {grant_type=refresh_token, refresh_token}
      |                       |<--(3.1) new access_token (+ optional new refresh_token)
```

### AIS Flow — Part 2: Account Information Queries

```
PSU (Customer)          TPP Application                              Bank Open API
      |                       |                                            |
      |---(4) Get accounts--->|                                            |
      |                       |---(4.1) GET /v1/accounts [Bearer token]--->|
      |                       |<--(4.2) accounts list----------------------|
      |<--(4.3) Display-------|                                            |
      |                       |                                            |
      |---(5) Get account info>|                                           |
      |                       |---(5.1) POST /v1/accounts/information----->|
      |                       |<--(5.2) account detail-----------------------|
      |<--(5.3) Display-------|                                            |
      |                       |                                            |
      |---(6) Get tx history-->|                                           |
      |                       |---(6.1) POST /v1/accounts/transactions---->|
      |                       |<--(6.2) transaction list---------------------|
      |<--(6.3) Display-------|                                            |
```

### AIS Consent Lifecycle

```
KH chưa consent / consent hết hạn (>180 days)
            |
            v
    GET /authorize (scope=AIS, response_type=code)
    → KH login + confirm consent → redirect with code
            |
            v
    POST /token (grant_type=authorization_code)
    → access_token + refresh_token
            |
            v
    [Use access_token for data APIs]
            |
    access_token expired?
     /              \
   Yes               No → continue using
    |
    v
  POST /token (grant_type=refresh_token)
  → new access_token (+ optional new refresh_token)
            |
    refresh_token expired (>180 days)?
     /              \
   Yes               No → continue refreshing
    |
    v
  Back to GET /authorize (KH must re-consent)

  [When KH withdraws consent on TPP app]
            |
            v
    POST /revoke → HTTP 200 OK, no body (RFC 7009)
```

### AIS Token Constraints

| Token/Value | Lifetime | Usage | Notes |
|---|---|---|---|
| Authorization Code | 180s | **Single use** | From `/authorize` redirect |
| access_token (authorization_code, AIS) | Max 3600s | Multiple use | For all data APIs (3.5–3.7) |
| refresh_token | Per consent duration (max 180 days, Article 11 Clause 6) | Multiple use | To get new access_token without re-consent |
| Consent duration | Max 180 days | — | Unless otherwise agreed between parties |

### AIS API Request/Response Summary

**3.1 GET /authorize** — Confirm & Get Consent:
- Query params: `response_type` = `"code"` (M), `client_id` (M), `scope` = `"AIS"` (M), `redirect_uri` (M), `state` (M), `code_challenge` (M), `code_challenge_method` = `"S256"` (O)
- Response (via redirect_uri): `code` (M), `state` (M)
- No `request` JWT parameter (unlike PIS which includes paymentId in JWT)

**3.2 POST /token** — Get Access Token:
- Auth: `Basic BASE64(client_id:client_secret)`
- Request: `grant_type` = `"authorization_code"` (M), `code` (M), `redirect_uri` (M), `code_verifier` (M)
- Response: `access_token` (M), `refresh_token` (M), `token_type` = `"Bearer"` (M), `expires_in` (M), `scope` (M)

**3.3 POST /token** — Refresh Access Token:
- Auth: `Basic BASE64(client_id:client_secret)`
- Request: `grant_type` = `"refresh_token"` (M), `refresh_token` (M), `scope` (O — must not exceed original scope)
- Response: `access_token` (M), `refresh_token` (O — may differ from original), `token_type` = `"Bearer"` (M), `expires_in` (M)

**3.4 POST /revoke** — Revoke Token (RFC 7009):
- Auth: `Basic BASE64(client_id:client_secret)`
- Request: `token` (M — value of access_token or refresh_token), `token_type_hint` (O — `"access_token"` or `"refresh_token"`)
- Response: HTTP 200 OK, no body (even if token is invalid, per RFC 7009)
- Called when customer withdraws data sharing consent on TPP application

**3.5 GET /v1/accounts** — Get List of Accounts:
- Auth: `Bearer access_token` (Authorization Code Grant, RFC 6749 Section 4.1)
- No query params, no request body
- Response: `accounts[]` → each: `identification` {`accountId` String[34]}, `name` (String[70]), `type` (String[4], ISO 20022), `currency` (String[3], ISO 4217), `bankCode` (String[8]), `additionalInfo` (Object, O)

**3.6 POST /v1/accounts/information** — Get Account Information:
- Request: `accountId` (String[34], M)
- Response: `identification` {`accountId`}, `name`, `type`, `currency`, `bankCode`, `creationDate` (DateTime), `balance[]` {`amount` {value, currency}, `dateTime`}, `additionalInfo` (O)

**3.7 POST /v1/accounts/transactions** — Get Transaction History:
- Request: `accountId` (String[34], M), `fromDate` (DateTime, M), `toDate` (DateTime, M), `page` (Number, O — starts from 1), `size` (Number, O)
- Response pagination: `pageCount`, `pageNumber`, `nextPage` (O), `pageSize`, `totalCount` (O)
- Response `transactions[]` → each: `amount` {value, currency}, `balance` {value, currency}, `creditDebitIndicator` (String[4] — `"CRDT"` or `"DBIT"`), `reversalIndicator` (Boolean, O), `valueDate` (DateTime), `references` {`instructionIdentification` String[70]}, `relatedParties` (O) {`debtor` {name, bankCode, accountId}, `creditor` {name, bankCode, accountId}}, `additionalTransactionInformation` (String[255]), `additionalInfo` (O)
- Query time range depends on Bank's regulations

### AIS Mandatory Headers

**Auth APIs** (3.1–3.4): `Content-Type: application/x-www-form-urlencoded`, `Authorization: Basic BASE64(client_id:client_secret)` (except /authorize which has no auth header), `Host` (O). **No JWS-Signature required.**

**Data APIs** (3.5–3.7) requests MUST include: `Content-Type: application/json`, `Authorization: Bearer {access_token}`, `Request-DateTime`, `Request-ID`, `Provider-ID`, `TPP-ID`, `JWS-Signature`. Optional: `PSU-IP-Address`, `PSU-User-Agent`, `PSU-Device-OS`, `Client-ID`.

**Data APIs** responses MUST echo: `Content-Type`, `Request-ID`, `Request-DateTime`, `JWS-Signature`.

**Reference**: Appendix 01, Section 3; Article 11, Clause 6 (consent duration)

**Verification**:
- Check that all 7 AIS endpoints exist with correct paths, HTTP methods, and Content-Types
- Check that auth APIs (3.1–3.4) use `x-www-form-urlencoded` and `Basic` auth, NOT `application/json`
- Check that auth APIs do NOT require JWS-Signature header
- Check that data APIs (3.5–3.7) use `Bearer` token from Authorization Code Grant (not client_credentials)
- Check that `/authorize` uses `response_type = "code"` (not `"code id_token"` like PIS) and scope `"AIS"`
- Check that `/authorize` does NOT include `request` JWT parameter (unlike PIS)
- Check that `/token` with `grant_type=authorization_code` returns both `access_token` AND `refresh_token`
- Check that refresh_token mechanism is implemented: `POST /token` with `grant_type=refresh_token`
- Check that token revocation is implemented per RFC 7009: `POST /revoke` returns 200 with no body
- Check that access_token lifetime is max 3600s and consent duration is max 180 days
- Check that transaction history API supports pagination (page starting from 1, size)
- Check that `creditDebitIndicator` uses ISO 20022 values: `"CRDT"` or `"DBIT"`
