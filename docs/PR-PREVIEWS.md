# PR preview deploys (Surge.sh)

Every pull request gets its own live preview of the generated site at
`https://lunatech-blog-pr-<number>.surge.sh`, rebuilt on each push and torn
down when the PR closes. The workflow is `.github/workflows/preview.yaml`.

Production (`blog.lunatech.com`) stays on GitHub Pages and is unaffected.

## One-time setup

The workflow skips itself (and stays green) until the Surge credentials are
configured as repository secrets.

1. Create a Surge account and get a token on any machine with Node installed:
   ```
   npx surge login      # use the email you want tied to the previews
   npx surge token       # prints the token
   ```
2. In the GitHub repo, add two Actions secrets
   (Settings > Secrets and variables > Actions):
   - `SURGE_LOGIN` the Surge account email from step 1
   - `SURGE_TOKEN` the token from step 1

That is all. The next push to any PR deploys a preview and the workflow posts
the URL as a PR comment.

## Notes

- The preview build overrides `site.url` to the preview domain, so canonical,
  Open Graph, RSS and sitemap links are self-consistent on the preview. The
  production `CNAME` is removed from the preview output so Surge does not try
  to publish to the custom domain.
- Previews from forked-repository PRs will not run, because forks cannot read
  repository secrets. Branches pushed to this repo work normally.
