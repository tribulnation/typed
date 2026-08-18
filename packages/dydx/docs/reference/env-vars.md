# Environment Variables

These are the environment variables read by dYdX wallet-aware constructors.

## Wallet Variables

```bash
DYDX_MNEMONIC=
DYDX_TESTNET_MNEMONIC=
```

## Guidance

- keep local values in an untracked `.env` file if needed
- load them explicitly in scripts and notebooks
- pass `public=True` when constructing read-only clients without a mnemonic
- mainnet node constructors read `DYDX_MNEMONIC`
- testnet node constructors read `DYDX_TESTNET_MNEMONIC`
