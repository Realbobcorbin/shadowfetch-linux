# GitHub Actions secrets

The release pipeline (`.github/workflows/build-iso.yml`) needs these secrets configured at
**Repo settings → Secrets and variables → Actions**:

| Secret | What | Where to get it |
|---|---|---|
| `RELEASE_GITHUB_TOKEN` | GitHub PAT used by `softprops/action-gh-release` to create signed releases. Needs `contents:write` on this repo. | github.com → Settings → Developer settings → Personal access tokens. **Already set.** |
| `SHADOWFETCH_GPG_PRIVATE_KEY` | ASCII-armored private key for the Shadowfetch APT/ISO signing key (fingerprint `8F13CE1535EE1F4A2916A1F73C5C900B7BE80CA1`). Used to sign the ISO and the reprepro repo. | Export from the build host with: `gpg --armor --export-secret-keys signing@shadowfetch.com`. **Not yet set.** |
| `R2_ACCESS_KEY_ID` | Access Key ID for an R2 API token scoped to `shadowfetch-linux` bucket (Object Read & Write). | Cloudflare dashboard → R2 → Manage R2 API Tokens → Create. **Not yet set.** (Old token used for manual publish should be rotated.) |
| `R2_SECRET_ACCESS_KEY` | Secret Access Key paired with `R2_ACCESS_KEY_ID`. | Shown once when token is created. **Not yet set.** |
| `CLOUDFLARE_API_TOKEN` | Cloudflare API token used by `wrangler deploy` to publish the `shadowfetch-linux` Worker. Needs Workers Scripts:Edit + Workers Routes:Edit + Workers KV:Edit on the account, on zone `shadowfetch.com`. | Cloudflare dashboard → My Profile → API Tokens → Create. **Not yet set.** |

## How the workflow triggers

- **Tag push (`v*`)**: full release pipeline — build ISO, sign, publish to R2, deploy Worker, create draft GitHub release.
- **Manual dispatch (`workflow_dispatch`)**: build only by default; choose `publish=true` to also publish + deploy. Useful for dry-runs.

## Cutting a release

```sh
git tag v1.0.1
git push origin v1.0.1
```

Workflow runs in CI. When it finishes (~60 min), publish the draft release in the GitHub UI.
