# Overview

- [Async Usage](async-usage.md)
- [Error Handling](error-handling.md)
- [Environment Variables](env-vars.md)
- [Timestamps](timestamps.md)

## Not Supported

The client leaves out the API types and channels that do nothing useful today:

1. Refused by the server: `/info` `alignedQuoteTokenInfo`; `/user` `getBalance`,
   `getDepositInfo`, `deposit`, `getTransaction` and `submitTransaction`; `/solana`
   `buildDepositTransaction`; the `activeAssetCtx`, `userFundings`,
   `userNonFundingLedgerUpdates`, `userTwapSliceFills` and `userTwapHistory` channels.
2. Accepted without effect: `/exchange` `twapOrder` and `updateIsolatedMargin`, and `/user`
   `submitEmail`, which carries no email.
3. Placeholder answers only: the `/info` types documented as "not yet populated"
   (`fundingHistory`, `predictedFundings`, `perpsAtOpenInterestCap`,
   `userNonFundingLedgerUpdates`, `userTWAPSliceFills`), the Hyperliquid-compatibility staking,
   vault, builder-DEX, role and builder-fee types (`perpDexStatus` excepted), and `portfolio`,
   `subAccounts`, `referral` and `userRateLimits`, which answer the same empty values for every
   account.
4. Never pushing: the `userEvents` and `notification` channels.

Their data is available elsewhere: `user.get_transfer_history` for the ledger,
`user.get_pnl_history` and `user.get_performance` for history, `user.get_referral_details` for
referrals, and `streams.user_fills` or `info.user_fills` for fills.
